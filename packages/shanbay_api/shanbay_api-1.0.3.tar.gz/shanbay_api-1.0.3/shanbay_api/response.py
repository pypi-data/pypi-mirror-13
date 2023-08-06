from rest_framework.response import Response
from shanbay_api import status as st

class Result(Response):
    status_code = st.SUCCESS
    
    def __init__(self, data={}, msg='', status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):

        status_code = status or self.status_code
        msg = msg or st.DEFAULT_MSG[status_code]
           
        wrapped_data = {
            'status_code': status_code,
            'msg': msg,
            'data': data
        }
        super(Result, self).__init__(wrapped_data, st.HTTP_200_OK,
                                     template_name, headers,
                                     exception, content_type)

SuccessResult = Result

class FailedResult(Result):
    status_code = st.FAILED

class BadRequestResult(Result):
    status_code = st.HTTP_400_BAD_REQUEST

class ForbiddenResult(Result):
    # we use 401 for forbidden result
    status_code = st.HTTP_401_UNAUTHORIZED
        
class NotFoundResult(Result):
    status_code = st.HTTP_404_NOT_FOUND

class DuplicatedResult(Result):
    status_code = st.HTTP_409_CONFLICT

class NotHereResult(Result):
    status_code = st.HTTP_410_GONE

class InternalErrorResult(Result):
    status_code = st.HTTP_500_INTERNAL_SERVER_ERROR

class RedirectResult(Result):
    status_code = st.HTTP_302_FOUND
