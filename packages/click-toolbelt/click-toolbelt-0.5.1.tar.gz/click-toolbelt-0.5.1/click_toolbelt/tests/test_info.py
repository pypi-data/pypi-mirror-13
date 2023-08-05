# -*- coding: utf-8 -*-
# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
from collections import namedtuple
from unittest import TestCase

from mock import call, patch

from click_toolbelt.common import CommandError
from click_toolbelt.info import (
    Info,
)


class InfoCommandTestCase(TestCase):

    def setUp(self):
        super(InfoCommandTestCase, self).setUp()
        app = None
        args = None
        self.command = Info(app, args)

        patcher = patch('click_toolbelt.info.Info.log')
        self.mock_log = patcher.start()
        self.addCleanup(patcher.stop)

        self.parsed_args = namedtuple('parsed_args', 'topic')
        self.args = self.parsed_args(None)

    def test_parser(self):
        parser = self.command.get_parser('prog_name')
        # only one argument -- the first item is the default help option
        self.assertEqual(len(parser._actions), 2)
        self.assertEqual(parser._actions[0].dest, 'help')
        # topic is optional
        self.assertEqual(parser._actions[1].dest, 'topic')
        self.assertFalse(parser._actions[1].required)

    def test_take_action(self):
        with patch('click_toolbelt.info.get_info') as mock_get_info:
            mock_get_info.return_value = {
                'success': True, 'errors': [], 'data': {'version': 1},
            }
            self.command.take_action(self.args)
        self.assertEqual(self.mock_log.info.call_args_list, [
            call('API info:'),
            call('  %s: %s', 'version', 1),
        ])

    def _test_take_action_with_topic(self, data, topic, expected):
        with patch('click_toolbelt.info.get_info') as mock_get_info:
            mock_get_info.return_value = {
                'success': True, 'errors': [], 'data': data,
            }
            args = self.parsed_args(topic)
            self.command.take_action(args)
        self.mock_log.info.assert_any_call('API info:')
        self.mock_log.info.assert_any_call(
            '  %s: %s', topic, expected)

    def test_take_action_with_version(self):
        data = {'version': 1}
        self._test_take_action_with_topic(data, 'version', 1)

    def test_take_action_with_department(self):
        expected = ['foo']
        data = {'department': expected}
        self._test_take_action_with_topic(data, 'department', expected)

    def test_take_action_with_license(self):
        expected = ['foo']
        data = {'license': expected}
        self._test_take_action_with_topic(data, 'license', expected)

    def test_take_action_with_country(self):
        expected = [['FO', 'foo']]
        data = {'country': expected}
        self._test_take_action_with_topic(data, 'country', expected)

    def test_take_action_with_channel(self):
        expected = ['stable', 'beta']
        data = {'channel': expected}
        self._test_take_action_with_topic(data, 'channel', expected)

    def test_take_action_with_error(self):
        with patch('click_toolbelt.info.get_info') as mock_get_info:
            mock_get_info.return_value = {
                'success': False, 'errors': ['some error'], 'data': None,
            }
            with self.assertRaises(CommandError):
                self.command.take_action(self.args)
        self.mock_log.info.assert_called_once_with(
            'Could not get information. An error ocurred:\n\n%s\n\n',
            'some error')
