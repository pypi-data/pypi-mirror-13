"""Django page CMS urls module."""

from django.conf.urls import url, patterns
from basic_cms.views import details
from basic_cms import settings
from basic_cms.api import BasicCMSAPI


urlpatterns = patterns(
    '',
    url(r'^basic-cms-api/(?P<slug>[-\w]+)/$', BasicCMSAPI.as_view(), name='basic_cms_api'),
)

if settings.PAGE_USE_LANGUAGE_PREFIX:
    urlpatterns += patterns('',
                            url(r'^(?P<lang>[-\w]+)/(?P<path>.*)$', details,
                                name='pages-details-by-path'),
                            # can be used to change the URL of the root page
                            # url(r'^$', details, name='pages-root')
                            )
else:
    urlpatterns += patterns('',
                            url(r'^(?P<path>.*)$', details, name='pages-details-by-path'),
                            # can be used to change the URL of the root page
                            # url(r'^$', details, name='pages-root'),
                            )
