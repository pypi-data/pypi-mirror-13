"""Tests for the models of the server_guardian app."""
from django.test import TestCase
from mixer.backend.django import mixer
from server_guardian import constants


class ServerTestCase(TestCase):
    """Tests for the ``Server`` model class."""
    longMessage = True

    def test_instantiation(self):
        server = mixer.blend('server_guardian.Server')
        self.assertTrue(server.pk)

    def test_get_response_dict(self):
        json_response = (
            '[{"label": "foobar", "status": "OK", "info": "it is OK"}]'
        )
        server = mixer.blend('server_guardian.Server',
                             response_body=json_response)
        self.assertEqual(
            server.get_parsed_response()[0]['status'],
            constants.SERVER_STATUS['OK'],
            msg=(
                'It should be possible to read the status from'
                ' the response dict.'
            )
        )
        self.assertEqual(
            server.get_parsed_response()[0]['info'],
            'it is OK',
            msg=(
                'It should be possible to read the info from the'
                ' response dict.'
            )
        )
        html_response = '<html><head></head><body>HTML RESPONSE</body></html>'
        server2 = mixer.blend('server_guardian.Server',
                              response_body=html_response)
        self.assertEqual(
            server2.get_parsed_response()[0]['status'],
            constants.SERVER_STATUS['DANGER'],
            msg=(
                'For an HTML response, the dict should return a'
                ' warning status.'
            )
        )

    def test_has_errors(self):
        # no error status
        json_response = (
            '[{"label": "foobar", "status": "OK", "info": "it is OK"}]'
        )
        server = mixer.blend('server_guardian.Server',
                             response_body=json_response)
        self.assertFalse(
            server.has_errors(),
            msg='The server should have no errors.')

        # error status
        json_response = (
            '[{"label": "foobar", "status": "OK", "info": "it is OK"}'
            '{"label": "barfoo", "status": "WARNING", "info": "oops"]'
        )
        server.response_body = json_response
        self.assertTrue(
            server.has_errors(),
            msg='The server should have an error.')

        # empty body and status code of 404
        json_response = ''
        server.response_body = json_response
        server.status_code = 404
        self.assertTrue(
            server.has_errors(),
            msg='The server should have an error.')
