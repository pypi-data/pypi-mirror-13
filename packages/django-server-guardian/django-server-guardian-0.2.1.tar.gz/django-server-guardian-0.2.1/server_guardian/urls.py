"""URLs for the server_guardian app."""
from compat import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^$',
        views.GuardianDashboardView.as_view(),
        name='server_guardian_dashboard'),
    url(r'^reload/$',
        views.GuardianReloadView.as_view(),
        name='server_guardian_reload'),
)
