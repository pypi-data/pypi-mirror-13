from __future__ import absolute_import, print_function, unicode_literals

import re

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from wagtail.contrib.wagtailsitemaps.views import sitemap
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailsearch.urls import frontend as wagtailsearch_frontend_urls

urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^search/', include(wagtailsearch_frontend_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^sitemap\.xml$', sitemap),
    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    def static(prefix, **kwargs):
        pattern = re.escape(prefix.lstrip('/')) + r'^%s(?P<path>.*)$'
        return [url(pattern, 'django.views.static.serve', kwargs=kwargs)]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
