"""Models for the server_guardian app."""
import json

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from compat import python_2_unicode_compatible

from . import constants


@python_2_unicode_compatible
class Server(models.Model):
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_('server name'),
    )
    url = models.URLField(
        verbose_name=_('API URL'),
        help_text='The URL, that the guardian API is available under.'
    )
    token = models.CharField(
        max_length=256,
        verbose_name=_('token'),
        help_text=(
            'Add this to your client server settings as'
            ' "SERVER_GUARDIAN_SECURITY_TOKEN".'
        ),
    )
    response_body = models.TextField(
        verbose_name=_('server response'),
        blank=True,
    )
    status_code = models.PositiveIntegerField(
        verbose_name=_('server response status code'),
        blank=True, null=True,
    )
    last_updated = models.DateTimeField(
        verbose_name=_('last updated'),
        blank=True, null=True,
    )

    def __unicode__(self):
        return self.__str__()

    def __str__(self):  # pragma: no cover
        if self.name:
            return self.name
        else:
            return self.url

    def get_absolute_url(self):
        return reverse('server_guardian_dashboard')

    def get_parsed_response(self):
        try:
            return json.loads(self.response_body)
        except ValueError:
            return constants.HTML_STATUS_FALLBACK

    def has_errors(self):
        for metric in self.get_parsed_response():
            if metric['status'] in constants.ERROR_STATUS:
                return True
        return False
