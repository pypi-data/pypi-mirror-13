from rest_framework.authentication import SessionAuthentication


class CSRFexemptSessionAuthentication(SessionAuthentication):
    """
    Use Django's session framework for authentication. without check csrf
    """
    def authenticate(self, request):
        request = request._request
        user = getattr(request, 'user', None)
        if not user or not user.is_active:
            return None
        return (user, None)

    def authenticate_header(self, request):
        """
        return some header so that rest_framework will generate a 401 Response
        if this return None, the framework will generate a 403 Response which we does't want
        """
        return "Authorization"
