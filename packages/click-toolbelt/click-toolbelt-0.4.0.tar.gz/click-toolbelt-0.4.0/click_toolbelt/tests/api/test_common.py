# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
import json
from unittest import TestCase

import responses
from mock import Mock, patch
from requests_oauthlib import OAuth1Session

from click_toolbelt.api.common import get_oauth_session, myapps_api_call


class GetOAuthSessionTestCase(TestCase):

    def setUp(self):
        super(GetOAuthSessionTestCase, self).setUp()
        patcher = patch(
            'click_toolbelt.api.common.load_config')
        self.mock_load_config = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_oauth_session_when_no_config(self):
        self.mock_load_config.return_value = {}
        session = get_oauth_session()
        self.assertIsNone(session)

    def test_get_oauth_session_when_partial_config(self):
        self.mock_load_config.return_value = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
        }
        session = get_oauth_session()
        self.assertIsNone(session)

    def test_get_oauth_session(self):
        self.mock_load_config.return_value = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
            'token_key': 'token-key',
            'token_secret': 'token-secret',
        }
        session = get_oauth_session()
        self.assertIsInstance(session, OAuth1Session)
        self.assertEqual(session.auth.client.client_key, 'consumer-key')
        self.assertEqual(session.auth.client.client_secret, 'consumer-secret')
        self.assertEqual(session.auth.client.resource_owner_key, 'token-key')
        self.assertEqual(session.auth.client.resource_owner_secret,
                         'token-secret')


class ApiCallTestCase(TestCase):

    def setUp(self):
        super(ApiCallTestCase, self).setUp()
        p = patch('click_toolbelt.api.common.os')
        mock_os = p.start()
        self.addCleanup(p.stop)
        mock_os.environ = {'MYAPPS_API_ROOT_URL': 'http://example.com'}

    @responses.activate
    def test_get_success(self):
        response_data = {'response': 'value'}
        responses.add(responses.GET, 'http://example.com/path',
                      json=response_data)

        result = myapps_api_call('/path')
        self.assertEqual(result, {
            'success': True,
            'data': response_data,
            'errors': [],
        })

    @responses.activate
    def test_get_error(self):
        response_data = {'response': 'error'}
        responses.add(responses.GET, 'http://example.com/path',
                      json=response_data, status=500)

        result = myapps_api_call('/path')
        self.assertEqual(result, {
            'success': False,
            'data': None,
            'errors': [json.dumps(response_data)],
        })

    @responses.activate
    def test_post_success(self):
        response_data = {'response': 'value'}
        responses.add(responses.POST, 'http://example.com/path',
                      json=response_data)

        result = myapps_api_call('/path', method='POST')
        self.assertEqual(result, {
            'success': True,
            'data': response_data,
            'errors': [],
        })

    @responses.activate
    def test_post_error(self):
        response_data = {'response': 'value'}
        responses.add(responses.POST, 'http://example.com/path',
                      json=response_data, status=500)

        result = myapps_api_call('/path', method='POST')
        self.assertEqual(result, {
            'success': False,
            'data': None,
            'errors': [json.dumps(response_data)],
        })

    def test_unsupported_method(self):
        self.assertRaises(ValueError, myapps_api_call, '/path', method='FOO')

    def test_get_with_session(self):
        session = Mock()
        myapps_api_call('/path', session=session)
        session.get.assert_called_once_with('http://example.com/path')

    def test_post_with_session(self):
        session = Mock()
        myapps_api_call('/path', method='POST', session=session)
        session.post.assert_called_once_with(
            'http://example.com/path',
            data=None, headers={'Content-Type': 'application/json'})

    @responses.activate
    def test_post_with_data(self):
        response_data = {'response': 'value'}
        responses.add(responses.POST, 'http://example.com/path',
                      json=response_data)

        result = myapps_api_call('/path', method='POST', data={'request': 'value'})
        self.assertEqual(result, {
            'success': True,
            'data': response_data,
            'errors': [],
        })
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['Content-Type'],
                         'application/json')
        self.assertEqual(responses.calls[0].request.body,
                         json.dumps({'request': 'value'}))
