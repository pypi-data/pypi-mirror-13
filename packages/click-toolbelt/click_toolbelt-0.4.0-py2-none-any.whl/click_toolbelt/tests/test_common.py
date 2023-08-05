# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
from unittest import TestCase

from mock import Mock, call, patch

from click_toolbelt.common import (
    Command,
    retry,
)
from click_toolbelt.tests.test_config import ConfigTestCase


class CommandTestCase(ConfigTestCase):
    command_class = Command

    def setUp(self):
        super(CommandTestCase, self).setUp()
        app = None
        args = None
        self.command = self.command_class(app, args)

        patcher = patch('click_toolbelt.api.common.get_oauth_session')
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


class RetryDecoratorTestCase(TestCase):

    def target(self, *args, **kwargs):
        return dict(args=args, kwargs=kwargs)

    def test_retry(self):
        result, aborted = retry()(self.target)()
        self.assertEqual(result, dict(args=(), kwargs={}))
        self.assertEqual(aborted, False)

    @patch('click_toolbelt.common.time.sleep')
    def test_retry_small_backoff(self, mock_sleep):
        mock_terminator = Mock()
        mock_terminator.return_value = False

        delay = 0.001
        result, aborted = retry(mock_terminator, retries=2,
                                delay=delay)(self.target)()

        self.assertEqual(result, dict(args=(), kwargs={}))
        self.assertEqual(aborted, True)
        self.assertEqual(mock_terminator.call_count, 3)
        self.assertEqual(mock_sleep.mock_calls, [
            call(delay),
            call(delay * 2),
        ])

    def test_retry_abort(self):
        mock_terminator = Mock()
        mock_terminator.return_value = False
        mock_logger = Mock()

        result, aborted = retry(mock_terminator, delay=0.001, backoff=1,
                                logger=mock_logger)(self.target)()

        self.assertEqual(result, dict(args=(), kwargs={}))
        self.assertEqual(aborted, True)
        self.assertEqual(mock_terminator.call_count, 4)
        self.assertEqual(mock_logger.warning.call_count, 3)

    def test_retry_with_invalid_retries(self):
        for value in (0.1, -1):
            with self.assertRaises(ValueError) as ctx:
                retry(retries=value)(self.target)
            self.assertEqual(
                str(ctx.exception),
                'retries value must be a positive integer or zero')

    def test_retry_with_negative_delay(self):
        with self.assertRaises(ValueError) as ctx:
            retry(delay=-1)(self.target)
        self.assertEqual(str(ctx.exception),
                         'delay value must be positive')

    def test_retry_with_invalid_backoff(self):
        for value in (-1, 0, 0.1):
            with self.assertRaises(ValueError) as ctx:
                retry(backoff=value)(self.target)
            self.assertEqual(str(ctx.exception),
                             'backoff value must be a positive integer')
