# -*- coding: utf-8 -*-
# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
from unittest import TestCase

from mock import patch

from storeapi.info import get_info


class InfoAPITestCase(TestCase):

    def setUp(self):
        super(InfoAPITestCase, self).setUp()

        patcher = patch('storeapi.common.requests.get')
        self.mock_get = patcher.start()
        self.mock_response = self.mock_get.return_value
        self.addCleanup(patcher.stop)

    def test_get_info(self):
        expected = {
            'success': True,
            'errors': [],
            'data': {'version': 1},
        }
        self.mock_response.ok = True
        self.mock_response.json.return_value = {'version': 1}
        data = get_info()
        self.assertEqual(data, expected)

    def test_get_info_with_error_response(self):
        expected = {
            'success': False,
            'errors': ['some error'],
            'data': None,
        }
        self.mock_response.ok = False
        self.mock_response.text = 'some error'
        data = get_info()
        self.assertEqual(data, expected)

    def test_get_info_uses_environment_variables(self):
        with patch('storeapi.common.os.environ',
                   {'MYAPPS_API_ROOT_URL': 'http://example.com'}):
            get_info()
        self.mock_get.assert_called_once_with('http://example.com')
