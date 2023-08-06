"""URLs to run the tests."""
from compat import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'', include('server_guardian.urls')),
    url(r'^api/', include('server_guardian_api.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
