# -*- coding: utf-8 -*-
# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
from unittest import TestCase

from mock import patch
from requests import Response

from click_toolbelt.api._login import login
from click_toolbelt.constants import (
    CLICK_TOOLBELT_PROJECT_NAME,
    UBUNTU_SSO_API_ROOT_URL,
)


class LoginAPITestCase(TestCase):

    def setUp(self):
        super(LoginAPITestCase, self).setUp()
        self.email = 'user@domain.com'
        self.password = 'password'

        # setup patches
        mock_environ = {
            'UBUNTU_SSO_API_ROOT_URL': UBUNTU_SSO_API_ROOT_URL,
        }
        patcher = patch('click_toolbelt.api._login.os.environ', mock_environ)
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('ssoclient.v2.http.requests.Session.request')
        self.mock_request = patcher.start()
        self.addCleanup(patcher.stop)
        self.token_data = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
            'token_key': 'token-key',
            'token_secret': 'token-secret',
        }
        response = self.make_response(status_code=201, reason='CREATED',
                                      data=self.token_data)
        self.mock_request.return_value = response

    def make_response(self, status_code=200, reason='OK', data=None):
        data = data or {}
        response = Response()
        response.status_code = status_code
        response.reason = reason
        response._content = json.dumps(data).encode('utf-8')
        return response

    def assert_login_request(self, otp=None,
                             token_name=CLICK_TOOLBELT_PROJECT_NAME):
        data = {
            'email': self.email,
            'password': self.password,
            'token_name': token_name
        }
        if otp is not None:
            data['otp'] = otp
        self.mock_request.assert_called_once_with(
            'POST', UBUNTU_SSO_API_ROOT_URL + 'tokens/oauth',
            data=json.dumps(data),
            json=None, headers={'Content-Type': 'application/json'}
        )

    def test_login_successful(self):
        result = login(self.email, self.password)
        expected = {'success': True, 'body': self.token_data}
        self.assertEqual(result, expected)

    def test_default_token_name(self):
        result = login(self.email, self.password)
        expected = {'success': True, 'body': self.token_data}
        self.assertEqual(result, expected)
        self.assert_login_request()

    def test_custom_token_name(self):
        result = login(self.email, self.password, token_name='my-token')
        expected = {'success': True, 'body': self.token_data}
        self.assertEqual(result, expected)
        self.assert_login_request(token_name='my-token')

    def test_login_with_otp(self):
        result = login(self.email, self.password, otp='123456')
        expected = {'success': True, 'body': self.token_data}
        self.assertEqual(result, expected)
        self.assert_login_request(otp='123456')

    def test_login_unsuccessful_api_exception(self):
        error_data = {
            'message': 'Error during login.',
            'code': 'INVALID_CREDENTIALS',
            'extra': {},
        }
        response = self.make_response(
            status_code=401, reason='UNAUTHORISED', data=error_data)
        self.mock_request.return_value = response

        result = login(self.email, self.password)
        expected = {'success': False, 'body': error_data}
        self.assertEqual(result, expected)

    def test_login_unsuccessful_unexpected_error(self):
        error_data = {
            'message': 'Error during login.',
            'code': 'UNEXPECTED_ERROR_CODE',
            'extra': {},
        }
        response = self.make_response(
            status_code=401, reason='UNAUTHORISED', data=error_data)
        self.mock_request.return_value = response

        result = login(self.email, self.password)
        expected = {'success': False, 'body': error_data}
        self.assertEqual(result, expected)
