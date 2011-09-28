from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # when invoking this url, specify a 'callback' GET param containing the callback url
    # optionally specify a 'format' GET param, corresponding to what format the Evernote authorization you want ('microclip' or 'mobile')
    url(r'^$',
        'siteapps_v1.google_oauth.views.oauth_start',
        name='oauth-start'
    ),
    url(r'^get_access_token/$',
        'siteapps_v1.google_oauth.views.oauth_get_access_token',
        name='oauth-get-access-token'
    ),
    url(r'^test/$',
        'siteapps_v1.google_oauth.views.oauth_test',
        name='test'
    ),
    url(r'^folder/(?P<resource_id>[a-z]+:[0-9a-zA-Z_\-]+)/$',
        'siteapps_v1.google_oauth.views.get_folder_contents',
        name='folder'
    ),
    url(r'^doc/(?P<resource_id>[a-z]+:[0-9a-zA-Z_\-]+)/$',
        'siteapps_v1.google_oauth.views.get_doc_content',
        name='doc'
    ),
)
