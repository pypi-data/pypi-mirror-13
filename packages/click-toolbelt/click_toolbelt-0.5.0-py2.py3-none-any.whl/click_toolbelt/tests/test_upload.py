# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import tempfile
from collections import namedtuple

from mock import patch

from click_toolbelt import __namespace__
from click_toolbelt.common import CommandError
from click_toolbelt.upload import (
    Upload,
)
from click_toolbelt.tests.test_common import (
    CommandTestCase,
)


class UploadCommandTestCase(CommandTestCase):
    command_class = Upload

    def setUp(self):
        super(UploadCommandTestCase, self).setUp()
        self.mock_get = self.mock_get_oauth_session.return_value.get
        self.mock_post = self.mock_get_oauth_session.return_value.post

        p = patch('storeapi._upload.logger')
        self.mock_logger = p.start()
        self.addCleanup(p.stop)
        p = patch('storeapi._upload.upload_files')
        self.mock_upload_files = p.start()
        self.addCleanup(p.stop)
        p = patch('storeapi._upload.upload_app')
        self.mock_upload_app = p.start()
        self.addCleanup(p.stop)

        self.package_name = 'namespace.binary'
        self.binary_filename = self.package_name + '_0.1_all.click'
        self.parsed_args = namedtuple(
            'parsed_args',
            'binary_filename, metadata_filename')
        self.args = self.parsed_args(self.binary_filename, None)

    def test_parser(self):
        parser = self.command.get_parser(__namespace__)
        # binary_filename is required
        self.assertEqual(parser._actions[1].dest, 'binary_filename')
        self.assertTrue(parser._actions[1].required)
        # metadata_filename is optional
        self.assertEqual(parser._actions[2].dest, 'metadata_filename')
        # this is a positional argument
        self.assertEqual(parser._actions[2].option_strings, [])
        self.assertFalse(parser._actions[2].required)
        self.assertEqual(parser._actions[3].dest, 'metadata_filename')
        # this is a named argument
        self.assertEqual(parser._actions[3].option_strings, ['--metadata'])
        self.assertFalse(parser._actions[3].required)

    def test_take_action(self):
        binary_filename = self.args.binary_filename

        self.command.take_action(self.args)

        self.mock_upload_files.assert_called_once_with(binary_filename)
        self.mock_upload_app.assert_called_once_with(
            self.package_name, self.mock_upload_files.return_value,
            metadata={})
        self.mock_logger.info.assert_any_call(
            'Application uploaded successfully.'
        )

    def test_take_action_works_for_snaps(self):
        binary_filename = self.package_name + '_0.1_all.snap'
        args = self.parsed_args(binary_filename, None)

        self.command.take_action(args)

        self.mock_upload_files.assert_called_once_with(binary_filename)
        self.mock_upload_app.assert_called_once_with(
            self.package_name, self.mock_upload_files.return_value,
            metadata={})
        self.mock_logger.info.assert_any_call(
            'Application uploaded successfully.'
        )

    def test_take_action_with_metadata_file(self):
        mock_metadata_file = tempfile.NamedTemporaryFile()
        with open(mock_metadata_file.name, 'wb') as mock_file:
            data = json.dumps({'changelog': 'some changes'})
            mock_file.write(data.encode('utf-8'))
            mock_file.flush()

        args = self.parsed_args(self.binary_filename,
                                mock_metadata_file.name)
        self.command.take_action(args)

        self.mock_upload_files.assert_called_once_with(
            self.binary_filename)
        self.mock_upload_app.assert_called_once_with(
            self.package_name, self.mock_upload_files.return_value,
            metadata={'changelog': 'some changes'})
        self.mock_logger.info.assert_any_call(
            'Application uploaded successfully.'
        )

    def test_take_action_with_metadata_file_without_source_file(self):
        mock_metadata_file = tempfile.NamedTemporaryFile()
        with open(mock_metadata_file.name, 'wb') as mock_file:
            data = json.dumps({'changelog': 'some changes'})
            mock_file.write(data.encode('utf-8'))
            mock_file.flush()

        args = self.parsed_args(self.binary_filename,
                                mock_metadata_file.name)
        self.command.take_action(args)

        self.mock_upload_files.assert_called_once_with(
            self.binary_filename)
        self.mock_upload_app.assert_called_once_with(
            self.package_name, self.mock_upload_files.return_value,
            metadata={'changelog': 'some changes'})
        self.mock_logger.info.assert_any_call(
            'Application uploaded successfully.'
        )

    def test_take_action_with_error_during_file_upload(self):
        binary_filename = self.args.binary_filename

        self.mock_upload_files.return_value = {
            'success': False,
            'errors': ['some error']
        }

        with self.assertRaises(CommandError):
            self.command.take_action(self.args)

        self.mock_upload_files.assert_called_once_with(
            binary_filename)
        self.assertFalse(self.mock_upload_app.called)
        self.mock_logger.info.assert_any_call(
            'Upload failed:\n\n%s\n', 'some error')

    def test_take_action_with_error_during_app_upload(self):
        binary_filename = self.args.binary_filename

        self.mock_upload_app.return_value = {
            'success': False,
            'errors': ['some error'],
        }

        with self.assertRaises(CommandError):
            self.command.take_action(self.args)

        self.mock_upload_files.assert_called_once_with(
            binary_filename)
        self.mock_upload_app.assert_called_once_with(
            self.package_name, self.mock_upload_files.return_value,
            metadata={})
        self.mock_logger.info.assert_any_call(
            'Upload did not complete.')
        self.mock_logger.info.assert_any_call(
            'Some errors were detected:\n\n%s\n\n',
            'some error')

    def test_take_action_with_invalid_package_name(self):
        args = self.parsed_args('binary', None)
        with self.assertRaises(CommandError):
            self.command.take_action(args)

        self.assertFalse(self.mock_upload_files.called)
        self.assertFalse(self.mock_upload_app.called)
        self.mock_logger.info.assert_any_call('Invalid package filename.')

    def test_take_action_shows_application_url(self):
        self.mock_upload_app.return_value = {
            'success': True,
            'errors': [],
            'application_url': 'http://example.com/',
        }

        self.command.take_action(self.args)

        self.mock_logger.info.assert_any_call(
            'Please check out the application at: %s.\n',
            'http://example.com/')
