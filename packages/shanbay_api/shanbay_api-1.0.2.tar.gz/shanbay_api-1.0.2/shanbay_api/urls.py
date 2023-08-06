import os
from django.conf.urls import url, include
from django.conf import settings

from shanbay_api.views import TestView, TestLoginRequiredView

# normal app api urls
urlpatterns = [(r'^%s/' % app, include('%s.api.urls' % app)) for app in settings.INSTALLED_APPS if os.path.exists('%s/%s/api/urls.py' % (settings.BASE_DIR, app))]

urlpatterns += [
    url('^test/$', TestView.as_view()),
    url('^login_required_test/$', TestLoginRequiredView.as_view())
]
