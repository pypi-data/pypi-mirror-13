"""Admin classes for the server_guardian app."""
from django.contrib import admin

from . import models


class ServerAdmin(admin.ModelAdmin):
    """Custom admin for the ``Server`` model."""
    list_display = ('name', 'url', 'status_code')
    fields = ('name', 'url', 'token')
    search_fields = ['name']


admin.site.register(models.Server, ServerAdmin)
