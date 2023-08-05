# -*- coding: utf-8 -*-
# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import tempfile
from collections import namedtuple

from mock import call, patch

from click_toolbelt.common import CommandError
from click_toolbelt.constants import MYAPPS_API_ROOT_URL
from click_toolbelt.channels import (
    Channels,
)
from click_toolbelt.tests.test_common import CommandTestCase


class ChannelsCommandTestCase(CommandTestCase):
    command_class = Channels

    def setUp(self):
        super(ChannelsCommandTestCase, self).setUp()

        patcher = patch('click_toolbelt.channels.Channels.log')
        self.mock_log = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_get = self.mock_get_oauth_session.return_value.get
        self.mock_post = self.mock_get_oauth_session.return_value.post

        self.parsed_args = namedtuple(
            'parsed_args', 'package_name, config_filename, publish')
        self.args = self.parsed_args('package.name', None, False)

        self.channels_data = [
            {'channel': 'stable', 'current': {'revision': 2, 'version': '1'}},
            {'channel': 'beta', 'current': {'revision': 4, 'version': '1.5'}},
            {'channel': 'edge', 'current': None},
        ]

    def assert_show_channels_status(self, errors=None):
        expected_calls = []

        if errors is None:
            errors = []
        for error in errors:
            error_call = call('ERROR: %s', error)
            expected_calls.append(error_call)

        channels = self.channels_data
        for config in channels:
            expected = None
            upload = config['current']
            if upload is not None:
                expected = 'Revision %d (version %s)' % (
                    upload['revision'], upload['version'])
            channel_call = call('%s: %s', config['channel'], expected)
            expected_calls.append(channel_call)
        self.assertEqual(self.mock_log.info.call_args_list, expected_calls)

    def assert_update(self, package_name, expected_data):
        self.mock_post.assert_called_once_with(
            '%spackage-channels/%s/' % (MYAPPS_API_ROOT_URL, package_name),
            data=json.dumps(expected_data),
            headers={'Content-Type': 'application/json'})

    def set_channels_get_success_response(self):
        mock_response = self.mock_get.return_value
        mock_response.ok = True
        mock_response.json.return_value = self.channels_data

    def set_channels_get_error_response(self, error_msg):
        mock_response = self.mock_get.return_value
        mock_response.ok = False
        mock_response.text = error_msg

    def set_channels_post_success_response(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True, 'errors': [], 'channels': self.channels_data
        }

    def set_channels_post_failed_response(self, error_msg):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True, 'errors': [error_msg],
            'channels': self.channels_data
        }

    def set_channels_post_error_response(self, error_msg):
        mock_response = self.mock_post.return_value
        mock_response.ok = False
        mock_response.text = error_msg

    def set_channels_config_file(self, data):
        mock_channels_file = tempfile.NamedTemporaryFile()
        with open(mock_channels_file.name, 'wb') as mock_file:
            data = json.dumps(data)
            mock_file.write(data.encode('utf-8'))
            mock_file.flush()
        return mock_channels_file

    def test_parser(self):
        parser = self.command.get_parser('prog_name')
        # only one argument -- the first item is the default help option
        self.assertEqual(len(parser._actions), 4)
        self.assertEqual(parser._actions[0].dest, 'help')
        # package_name is required
        self.assertEqual(parser._actions[1].dest, 'package_name')
        self.assertTrue(parser._actions[1].required)
        # config_filename is optional
        self.assertEqual(parser._actions[2].dest, 'config_filename')
        self.assertFalse(parser._actions[2].required)
        # publish is optional
        self.assertEqual(parser._actions[3].dest, 'publish')
        self.assertFalse(parser._actions[3].required)

    def test_get_channels_config_from_file(self):
        channels = {'stable': 2, 'beta': 1}
        mock_channels_file = self.set_channels_config_file(channels)

        config = self.command.get_channels_config(
            mock_channels_file.name, False)

        expected = {'channels': channels, 'publish': False}
        self.assertEqual(config, expected)

    def test_get_channels_config_no_file(self):
        config = self.command.get_channels_config(None, False)

        expected = {'channels': {}, 'publish': False}
        self.assertEqual(config, expected)

    def test_get_channels_config_do_publish(self):
        config = self.command.get_channels_config(None, True)

        expected = {'channels': {}, 'publish': True}
        self.assertEqual(config, expected)

    def test_get_channels_config_from_file_and_do_publish(self):
        channels = {'stable': 2, 'beta': 1}
        mock_channels_file = self.set_channels_config_file(channels)

        config = self.command.get_channels_config(
            mock_channels_file.name, True)

        expected = {'channels': channels, 'publish': True}
        self.assertEqual(config, expected)

    def test_show_channels(self):
        self.command.show_channels(self.channels_data)
        self.assert_show_channels_status()

    def test_take_action_invalid_credentials(self):
        self.mock_get_oauth_session.return_value = None

        with self.assertRaises(CommandError):
            self.command.take_action(self.args)

        self.mock_log.info.assert_called_once_with(
            'No valid credentials found.')

    def test_take_action_no_update(self):
        self.set_channels_get_success_response()

        self.command.take_action(self.args)

        self.assert_show_channels_status()

    def test_take_action_with_error(self):
        error_msg = 'some error'
        self.set_channels_get_error_response(error_msg)

        with self.assertRaises(CommandError):
            self.command.take_action(self.args)

        self.mock_log.info.assert_called_once_with(
            'Could not get information. An error ocurred:\n\n%s\n\n',
            'some error')

    def test_take_action_update_with_error(self):
        error_msg = 'some error'
        self.set_channels_post_error_response(error_msg)

        args = self.parsed_args('package.name', None, True)
        with self.assertRaises(CommandError):
            self.command.take_action(args)

        self.mock_log.info.assert_called_once_with(
            'Could not get information. An error ocurred:\n\n%s\n\n',
            'some error')

    def test_take_action_update_publish(self):
        self.set_channels_post_success_response()

        args = self.parsed_args('package.name', None, True)
        self.command.take_action(args)

        expected = {'channels': {}, 'publish': True}
        self.assert_update('package.name', expected)
        self.assert_show_channels_status()

    def test_take_action_update_channels(self):
        self.set_channels_post_success_response()
        channels = {'stable': 2, 'beta': 1}
        mock_channels_file = self.set_channels_config_file(channels)

        args = self.parsed_args('package.name', mock_channels_file.name, False)
        self.command.take_action(args)

        expected = {'channels': channels, 'publish': False}
        self.assert_update('package.name', expected)
        self.assert_show_channels_status()

    def test_take_action_update_channels_and_publish(self):
        self.set_channels_post_success_response()
        channels = {'stable': 2, 'beta': 1}
        mock_channels_file = self.set_channels_config_file(channels)

        args = self.parsed_args('package.name', mock_channels_file.name, True)
        self.command.take_action(args)

        expected = {'channels': channels, 'publish': True}
        self.assert_update('package.name', expected)
        self.assert_show_channels_status()

    def test_take_action_update_channels_fails(self):
        self.set_channels_post_failed_response('some error')

        args = self.parsed_args('package.name', None, True)
        self.command.take_action(args)

        expected = {'channels': {}, 'publish': True}
        self.assert_update('package.name', expected)
        self.assert_show_channels_status(errors=['some error'])
