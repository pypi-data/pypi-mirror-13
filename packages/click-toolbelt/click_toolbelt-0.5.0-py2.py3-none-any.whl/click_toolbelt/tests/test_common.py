# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals

from mock import patch

from click_toolbelt.common import (
    Command,
)
from click_toolbelt.tests.test_config import ConfigTestCase


class CommandTestCase(ConfigTestCase):
    command_class = Command

    def setUp(self):
        super(CommandTestCase, self).setUp()
        app = None
        args = None
        self.command = self.command_class(app, args)

        patcher = patch('click_toolbelt.common.get_oauth_session')
        self.mock_get_oauth_session = patcher.start()
        self.addCleanup(patcher.stop)

    def test_proxy_get_oauth_session(self):
        session = self.command.get_oauth_session()
        self.assertEqual(session, self.mock_get_oauth_session.return_value)

    @patch('click_toolbelt.common.load_config')
    def test_proxy_load_config(self, mock_load_config):
        config = self.command.load_config()
        self.assertEqual(config, mock_load_config.return_value)

    @patch('click_toolbelt.common.save_config')
    def test_proxy_save_config(self, mock_save_config):
        data = {}
        self.command.save_config(data)
        mock_save_config.assert_called_once_with(data)

    @patch('click_toolbelt.common.clear_config')
    def test_proxy_clear_config(self, mock_clear_config):
        self.command.clear_config()
        mock_clear_config.assert_called_once_with()
