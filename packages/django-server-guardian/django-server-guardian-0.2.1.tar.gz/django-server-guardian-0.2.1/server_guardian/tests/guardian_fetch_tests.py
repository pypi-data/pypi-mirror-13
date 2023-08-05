"""Tests for the ``guardian_fetch`` command."""
import requests
from collections import namedtuple

from django.core import mail
from django.core.management import call_command
from django.test import TestCase

import mock

from .mixes import new_server_factory
from ..constants import SERVER_STATUS
from ..models import Server


class CommandTestCase(TestCase):
    """Test case for the ``guardian_fetch`` command."""
    longMessage = True

    def setUp(self):
        self.server = new_server_factory()
        self.server_response = namedtuple(
            'response',
            ['status_code', 'content']
        )
        self.get_mock = requests.get

    def tearDown(self):
        requests.get = self.get_mock

    def test_command(self):
        self.server_response.status_code = 200
        json_response = (
            '[{"label": "foobar", "status": "OK", "info": "it is OK"}]'
        )
        self.server_response.content = json_response
        requests.get = mock.MagicMock(
            return_value=self.server_response,
        )
        call_command('guardian_fetch')
        server = Server.objects.get(pk=self.server.pk)
        self.assertEqual(
            server.get_parsed_response()[0]['status'],
            SERVER_STATUS['OK'],
            msg=(
                'After the command was run, the server instance should have'
                ' an updated status of "OK".'
            )
        )

        self.server_response.status_code = 404
        requests.get = mock.MagicMock(
            return_value=self.server_response,
        )
        call_command('guardian_fetch')
        self.assertEqual(len(mail.outbox), 1, msg=(
            'There should be one email sent, because the server responsed with'
            ' a code of 404.'
        ))

        mail.outbox = []
        self.server_response.status_code = 200
        self.server_response.content = 'this is not JSON'
        requests.get = mock.MagicMock(
            return_value=self.server_response,
        )
        call_command('guardian_fetch')
        self.assertEqual(len(mail.outbox), 1, msg=(
            'There should be one email sent if the response is not JSON.'
        ))

        mail.outbox = []
        self.server_response.status_code = 200
        self.server_response.content = '{"wrong": "JSON data"}'
        requests.get = mock.MagicMock(
            return_value=self.server_response,
        )
        call_command('guardian_fetch')
        self.assertEqual(len(mail.outbox), 1, msg=(
            'There should be one email sent if the response is JSON, but in'
            ' the wrong format.'
        ))
