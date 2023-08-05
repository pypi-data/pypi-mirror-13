# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import os
import tempfile
from unittest import TestCase

from mock import ANY, patch
from requests import Response

from storeapi._upload import (
    get_upload_url,
    upload_app,
    upload_files,
    upload,
)


class UploadBaseTestCase(TestCase):

    def setUp(self):
        super(UploadBaseTestCase, self).setUp()

        # setup patches
        name = 'storeapi._upload.get_oauth_session'
        patcher = patch(name)
        self.mock_get_oauth_session = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_get = self.mock_get_oauth_session.return_value.get
        self.mock_post = self.mock_get_oauth_session.return_value.post

        self.suffix = '_0.1_all.click'
        self.binary_file = self.get_temporary_file(suffix=self.suffix)

    def get_temporary_file(self, suffix='.cfg'):
        return tempfile.NamedTemporaryFile(suffix=suffix)


class UploadWithScanTestCase(UploadBaseTestCase):

    def test_default_metadata(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'successful': True,
            'upload_id': 'some-valid-upload-id',
        }

        upload(self.binary_file.name)

        data = {
            'updown_id': 'some-valid-upload-id',
            'source_uploaded': False,
            'binary_filesize': 0,
        }
        name = os.path.basename(self.binary_file.name).replace(self.suffix, '')
        self.mock_post.assert_called_with(
            get_upload_url(name), data=data, files=[])

    def test_metadata_from_file(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'successful': True,
            'upload_id': 'some-valid-upload-id',
        }

        with self.get_temporary_file() as metadata_file:
            data = json.dumps({'name': 'from_file'})
            metadata_file.write(data.encode('utf-8'))
            metadata_file.flush()

            upload(
                self.binary_file.name, metadata_filename=metadata_file.name)

        data = {
            'updown_id': 'some-valid-upload-id',
            'source_uploaded': False,
            'binary_filesize': 0,
            'name': 'from_file',
        }
        name = os.path.basename(self.binary_file.name).replace(self.suffix, '')
        self.mock_post.assert_called_with(
            get_upload_url(name), data=data, files=[])

    def test_override_metadata(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'successful': True,
            'upload_id': 'some-valid-upload-id',
        }

        upload(
            self.binary_file.name, metadata={'name': 'overridden'})

        data = {
            'updown_id': 'some-valid-upload-id',
            'source_uploaded': False,
            'binary_filesize': 0,
            'name': 'overridden',
        }
        name = os.path.basename(self.binary_file.name).replace(self.suffix, '')
        self.mock_post.assert_called_with(
            get_upload_url(name), data=data, files=[])


class UploadFilesTestCase(UploadBaseTestCase):

    def setUp(self):
        super(UploadFilesTestCase, self).setUp()
        self.binary_file = self.get_temporary_file(suffix='_0.1_all.click')

    def test_upload_files(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'successful': True,
            'upload_id': 'some-valid-upload-id',
        }

        response = upload_files(self.binary_file.name)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'upload_id': 'some-valid-upload-id',
            'binary_filesize': os.path.getsize(self.binary_file.name),
            'source_uploaded': False,
        })

    def test_upload_files_uses_environment_variables(self):
        with patch.dict(os.environ,
                        CLICK_UPDOWN_UPLOAD_URL='http://example.com'):
            upload_url = 'http://example.com/unscanned-upload/'
            upload_files(self.binary_file.name)
            self.mock_post.assert_called_once_with(
                upload_url, files={'binary': ANY})

    def test_upload_files_with_source_upload(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'successful': True,
            'upload_id': 'some-valid-upload-id',
        }

        response = upload_files(self.binary_file.name)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'upload_id': 'some-valid-upload-id',
            'binary_filesize': os.path.getsize(self.binary_file.name),
            'source_uploaded': False,
        })

    def test_upload_files_with_invalid_oauth_session(self):
        self.mock_get_oauth_session.return_value = None
        response = upload_files(self.binary_file.name)
        self.assertEqual(response, {
            'success': False,
            'errors': ['No valid credentials found.'],
        })
        self.assertFalse(self.mock_post.called)

    def test_upload_files_error_response(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = False
        mock_response.reason = '500 INTERNAL SERVER ERROR'
        mock_response.text = 'server failed'

        response = upload_files(self.binary_file.name)
        self.assertEqual(response, {
            'success': False,
            'errors': ['server failed'],
        })

    def test_upload_files_handle_malformed_response(self):
        mock_response = self.mock_post.return_value
        mock_response.json.return_value = {'successful': False}

        response = upload_files(self.binary_file.name)
        err = KeyError('upload_id')
        self.assertEqual(response, {
            'success': False,
            'errors': [str(err)],
        })


class UploadAppTestCase(UploadBaseTestCase):

    def setUp(self):
        super(UploadAppTestCase, self).setUp()
        self.data = {
            'upload_id': 'some-valid-upload-id',
            'binary_filesize': 123456,
            'source_uploaded': False,
        }
        self.package_name = 'namespace.binary'

        patcher = patch.multiple(
            'storeapi._upload',
            SCAN_STATUS_POLL_DELAY=0.0001)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_upload_app_with_invalid_oauth_session(self):
        self.mock_get_oauth_session.return_value = None
        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': ['No valid credentials found.'],
            'application_url': '',
            'revision': None,
        })

    def test_upload_app_uses_environment_variables(self):
        with patch.dict(os.environ,
                        MYAPPS_API_ROOT_URL='http://example.com'):
            upload_url = ("http://example.com/click-package-upload/%s/" %
                          self.package_name)
            data = {
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
            }
            upload_app(self.package_name, self.data)
            self.mock_post.assert_called_once_with(
                upload_url, data=data, files=[])

    def test_upload_app(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/'
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': True,
            'revision': 15,
        }

        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'application_url': '',
            'revision': 15,
        })

    def test_upload_app_error_response(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = False
        mock_response.reason = '500 INTERNAL SERVER ERROR'
        mock_response.text = 'server failure'

        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': ['server failure'],
            'application_url': '',
            'revision': None,
        })

    def test_upload_app_handle_malformed_response(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {}

        response = upload_app(self.package_name, self.data)
        err = KeyError('status_url')
        self.assertEqual(response, {
            'success': False,
            'errors': [str(err)],
            'application_url': '',
            'revision': None,
        })

    def test_upload_app_with_errors_during_scan(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/'
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': True,
            'message': 'some error',
            'application_url': 'http://example.com/myapp',
        }

        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': ['some error'],
            'application_url': 'http://example.com/myapp',
            'revision': None,
        })

    def test_upload_app_poll_status(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/'
        }

        response_not_completed = Response()
        response_not_completed.status_code = 200
        response_not_completed.encoding = 'utf-8'
        response_not_completed._content = json.dumps(
            {'completed': False, 'application_url': ''}).encode('utf-8')
        response_completed = Response()
        response_completed.status_code = 200
        response_completed.encoding = 'utf-8'
        response_completed._content = json.dumps(
            {'completed': True, 'revision': 14,
             'application_url': 'http://example.org'}).encode('utf-8')
        self.mock_get.side_effect = [
            response_not_completed,
            response_not_completed,
            response_completed,
        ]
        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'application_url': 'http://example.org',
            'revision': 14,
        })
        self.assertEqual(self.mock_get.call_count, 3)

    def test_upload_app_ignore_non_ok_responses(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/',
        }

        ok_response = Response()
        ok_response.status_code = 200
        ok_response.encoding = 'utf-8'
        ok_response._content = json.dumps(
            {'completed': True, 'revision': 14}).encode('utf-8')
        nok_response = Response()
        nok_response.status_code = 503

        self.mock_get.side_effect = [nok_response, nok_response, ok_response]
        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'application_url': '',
            'revision': 14,
        })
        self.assertEqual(self.mock_get.call_count, 3)

    def test_upload_app_abort_polling(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/',
            'web_status_url': 'http://example.com/status-web/',
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': False
        }
        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': [
                'Package scan took too long.',
                'Please check the status later at: '
                'http://example.com/status-web/.',
            ],
            'application_url': '',
            'revision': None,
        })

    def test_upload_app_abort_polling_without_web_status_url(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/',
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': False
        }
        response = upload_app(self.package_name, self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': [
                'Package scan took too long.',
            ],
            'application_url': '',
            'revision': None,
        })

    def test_upload_app_with_metadata(self):
        upload_app(self.package_name, self.data, metadata={
            'changelog': 'some changes', 'tagline': 'a tagline'})
        self.mock_post.assert_called_once_with(
            ANY,
            data={
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
                'changelog': 'some changes',
                'tagline': 'a tagline',
            },
            files=[],
        )

    def test_upload_app_ignore_special_attributes_in_metadata(self):
        upload_app(
            self.package_name,
            self.data, metadata={
                'changelog': 'some changes',
                'tagline': 'a tagline',
                'upload_id': 'my-own-id',
                'binary_filesize': 0,
                'source_uploaded': False,
            })
        self.mock_post.assert_called_once_with(
            ANY,
            data={
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
                'changelog': 'some changes',
                'tagline': 'a tagline',
            },
            files=[],
        )

    @patch('storeapi._upload.open')
    def test_upload_app_with_icon(self, mock_open):
        with tempfile.NamedTemporaryFile() as icon:
            mock_open.return_value = icon

            upload_app(
                self.package_name, self.data,
                metadata={
                    'icon_256': icon.name,
                }
            )
            self.mock_post.assert_called_once_with(
                ANY,
                data={
                    'updown_id': self.data['upload_id'],
                    'binary_filesize': self.data['binary_filesize'],
                    'source_uploaded': self.data['source_uploaded'],
                },
                files=[
                    ('icon_256', icon),
                ],
            )

    @patch('storeapi._upload.open')
    def test_upload_app_with_screenshots(self, mock_open):
        screenshot1 = tempfile.NamedTemporaryFile()
        screenshot2 = tempfile.NamedTemporaryFile()
        mock_open.side_effect = [screenshot1, screenshot2]

        upload_app(
            self.package_name, self.data,
            metadata={
                'screenshots': [screenshot1.name, screenshot2.name],
            }
        )
        self.mock_post.assert_called_once_with(
            ANY,
            data={
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
            },
            files=[
                ('screenshots', screenshot1),
                ('screenshots', screenshot2),
            ],
        )

    def test_get_upload_url(self):
        with patch.dict(os.environ,
                        MYAPPS_API_ROOT_URL='http://example.com'):
            upload_url = "http://example.com/click-package-upload/app.dev/"
            url = get_upload_url('app.dev')
            self.assertEqual(url, upload_url)
