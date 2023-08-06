import re
from functools import wraps

from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.utils import OperationalError
from django.utils.translation import ugettext as _
from django.utils import six
from django.views.decorators.csrf import csrf_exempt

from rest_framework import exceptions
from rest_framework.views import APIView as RestView
from rest_framework.renderers import JSONRenderer
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from shanbay_api.response import Result, FailedResult, ForbiddenResult, NotFoundResult
from shanbay_api.exceptions import DataFormatError, IllegalMixCollation
from shanbay_api.authentication import CSRFexemptSessionAuthentication


METHODS = re.compile(r'(?:get|post|put|delete)\(\)')

class IgnoreClientContentNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix):
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        return (renderers[0], renderers[0].media_type)

def api_permission_required(perm, msg=_('permission required')):
    """
    add Django permission check to specify view method
    usage:
        @api_permission_required('read.add_article')
        def create(self, request, *args, **kwargs):

    """
    def decorator(method):
        @wraps(method)
        def _wrapped_method(self, request, *args, **kwargs):
            user = request.user
            if perm == 'auth':
                if not user.is_authenticated():
                    raise exceptions.NotAuthenticated()
            elif perm == 'staff':
                if not user.is_staff:
                    raise exceptions.NotAuthenticated()
            elif not user.has_perm(perm):
                raise PermissionDenied()

            return method(self, request, *args, **kwargs)

        return _wrapped_method

    return decorator

def exception_handler(exc):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's builtin `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause Result with status=status.FAILED.
    """
    if isinstance(exc, Http404):
        msg = getattr(exc, 'msg', 'Not Found')
        return NotFoundResult(msg=msg)

    if isinstance(exc, OperationalError):
        if exc.args and exc.args[0] == IllegalMixCollation:
            return FailedResult()

    elif isinstance(exc, DataFormatError):
        msg = getattr(exc, 'msg', 'data format error')
        return FailedResult(msg=msg)

    elif isinstance(exc, TypeError):
        # user request an API with unexpected keyword argument
        # this happend when 'GET' and 'POST' method has different arguments
        # and user reqeust a 'GET' url with 'POST', or conversely
        msg = str(exc)
        if METHODS.match(msg):
            return FailedResult(msg=_('Bad Request. API got an unexpected argument'))

        raise

    elif isinstance(exc, PermissionDenied) or isinstance(exc, exceptions.PermissionDenied):
        return ForbiddenResult()

    elif isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['X-Throttle-Wait-Seconds'] = '%d' % exc.wait

        return Response({'msg':exc.detail},
                      status=exc.status_code,
                      headers=headers)

    # Note: Unhandled exceptions will raise a 500 error.
    return None

def get_view_name(cls):
    name = cls.__name__
    return  re.sub(r"([A-Z])", lambda mo: "_" + mo.group(0).lower(), name)[1:]

class APIView(RestView):
    content_negotiation_class = IgnoreClientContentNegotiation
    render_classes = (JSONRenderer,)
    permission_classes = (IsAuthenticated, )
    authentication_classes = (CSRFexemptSessionAuthentication, )

    max_ids_length = 50
    max_page_num = 100
    max_page_items = 50
    item_per_page = 10
    perms = {'allowany': (AllowAny, )}

    def get_permissions(self):
        """
        custom this method for setting AllowAny conveniently
        """
        if isinstance(self.permission_classes, six.string_types):
            key = self.permission_classes.lower()
            self.permission_classes = self.perms[key]

        return super(APIView, self).get_permissions()

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        super(APIView, self).dispatch(request, *args, **kwargs)
        if self.response is None:
            self.response = Result()
        return self.response

    def data(self, request):
        if request.method == 'GET':
            data = request.GET
        else:
            try:
                data = request.DATA
            except AttributeError:
                data = {}
        return data or {}

    def get_int_data(self, *fields):
        data = self.data(self.request)
        values = []
        for field in fields:
            try:
                value = int(data.get(field))
                values.append(value)
            except (TypeError, ValueError):
                raise DataFormatError()
        if len(fields) > 1:
            return values
        else:
            return values[0]

    def get_page(self, request):
        try:
            page = int(request.GET.get('page',1))
            page = max(page, 1)
        except (ValueError, TypeError):
            page = 1

        self.page = page
        return page

    def get_ipp(self, request):
        if 'ipp' not in request.GET:
            return self.item_per_page

        try:
            ipp = int(request.GET.get('ipp'))
            if ipp > self.max_page_items or ipp < 0:
                ipp = self.max_page_items
        except (TypeError, ValueError):
            ipp = self.item_per_page

        return ipp

    @staticmethod
    def key_of_cached_contents(key_prefix, page, ipp, reverse):
        return '{key_prefix}.{page:d}.{ipp:d}.{reverse:d}'.format(key_prefix=key_prefix,
                                                            page=page,
                                                            ipp=ipp,
                                                            reverse=reverse)

    def process_contents(self, contents, reverse):
        try:
            total = contents.count()
            if reverse:
                # queyrset.reverse return a new queryset
                contents = contents.reverse()
        except (AttributeError, TypeError):
            total = len(contents)
            # list.reverse modify content in-place
            reverse and contents.reverse()
        return total, contents

    def paginate_result(self, objects, contents_key='objects'):
        """
        this is a shortcut method for self.pagination
        for most of time ,we will call `return Result(data:{'total':total, 'ipp':ipp, 'data':data})`
        """
        total, ipp, contents = self.pagination(objects)
        return Result(data={'total':total, 'ipp':ipp, contents_key:contents})

    def pagination(self, contents, **kwargs):
        page = kwargs.get('page', self.get_page(self.request))
        ipp = self.get_ipp(self.request)

        reverse = 'reverse' in self.request.GET
        total, contents = self.process_contents(contents, reverse)
        if page > self.max_page_num:
            return total,ipp,[]

        contents = list(contents[ipp*(page-1):ipp*page])
        if reverse:
            contents.reverse()
        return total, ipp, contents

    def validate_ids(self, ids=None, seperator=','):
        if ids is None:
            ids = self.request.GET.get('ids')

        try:
            ids = [int(i) for i in ids.split(seperator)]
        except (TypeError, ValueError, AttributeError):
            raise DataFormatError(msg=_('ids format error'))

        if len(ids) > self.max_ids_length:
            raise DataFormatError(msg=_('ids too long'))

        return ids

    @classmethod
    def get_view_name(cls):
        name = cls.__name__
        return  re.sub(r"([A-Z])", lambda mo: "_" + mo.group(0).lower(), name)[1:]

    # this is almost same with django's get_object_or_404,
    # which will call `get` with a `queryset` (queryset.get)
    # but if we custom the `get` method like in Learning, the customed method will not be called
    # so this function is still needed
    @staticmethod
    def get_model_or_404(Model, msg=_('Not Found'), cached=False, **kwargs):
        if cached:
            model = cache.get_model(Model, **kwargs)
        else:
            model = Model.objects.get(**kwargs)

        return model

class TestLoginRequiredView(APIView):
    pass

class TestView(APIView):
    permission_classes = 'allowany'

    def get(self, request):
        return Result()
    def post(self, request):
        return FailedResult()
