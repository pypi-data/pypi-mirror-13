=====
Shanbay API Framework
=====


Quick start
-----------

1. Install ``shanbay_api`` by pip::
    
    pip install shanbay_api

2. Add ``'shanbay_api'`` to your ``INSTALLED_APPS`` setting like this::

    INSTALLED_APPS = (
    ...
    'shanbay_api',
    )
    
3. Include ``'shanbay_api.urls'`` in your project urls

    urlpatterns += ['^api/v2', include('shanbay_api.urls')]
    
4. Use ``APIView`` in shanbay-api