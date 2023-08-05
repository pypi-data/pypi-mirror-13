# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import os
import tempfile
from unittest import TestCase

from mock import patch

import click_toolbelt.config
from click_toolbelt.compat import ConfigParser
from click_toolbelt.config import clear_config, load_config, save_config


class ConfigTestCase(TestCase):

    def setUp(self):
        super(ConfigTestCase, self).setUp()

        patcher = patch('click_toolbelt.config.load_first_config')
        self.mock_load_first_config = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.config.save_config_path')
        self.mock_save_config_path = patcher.start()
        self.addCleanup(patcher.stop)

        cfg_file = self.get_temporary_file()
        self.filename = cfg_file.name
        config_dir = os.path.dirname(self.filename)
        self.mock_load_first_config.return_value = config_dir
        self.mock_save_config_path.return_value = config_dir

        patcher = patch.object(
            click_toolbelt.config, '__namespace__',
            os.path.basename(os.path.splitext(self.filename)[0]))
        patcher.start()
        self.addCleanup(patcher.stop)

        # make sure env is not overwritten
        patcher = patch.object(os, 'environ', {})
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_temporary_file(self, suffix='.cfg'):
        return tempfile.NamedTemporaryFile(suffix=suffix)


class LoadConfigTestCase(ConfigTestCase):

    def test_load_config_with_no_existing_file(self):
        data = load_config()
        self.assertEqual(data, {})

    def test_load_config_with_no_existing_section(self):
        cfg = ConfigParser()
        cfg.add_section('some.domain')
        cfg.set('some.domain', 'foo', '1')
        with open(self.filename, 'w') as fd:
            cfg.write(fd)

        data = load_config()
        self.assertEqual(data, {})

    def test_load_config(self):
        cfg = ConfigParser()
        cfg.add_section('login.ubuntu.com')
        cfg.set('login.ubuntu.com', 'foo', '1')
        with open(self.filename, 'w') as fd:
            cfg.write(fd)

        data = load_config()
        self.assertEqual(data, {'foo': '1'})


class SaveConfigTestCase(ConfigTestCase):

    def test_save_config_with_no_existing_file(self):
        data = {'key': 'value'}

        save_config(data)
        self.assertEqual(load_config(), data)

    def test_save_config_with_existing_file(self):
        cfg = ConfigParser()
        cfg.add_section('some.domain')
        cfg.set('some.domain', 'foo', '1')
        with open(self.filename, 'w') as fd:
            cfg.write(fd)

        data = {'key': 'value'}
        save_config(data)

        config = load_config()
        self.assertEqual(config, data)


class ClearConfigTestCase(ConfigTestCase):

    def test_clear_config_with_no_existing_section(self):
        cfg = ConfigParser()
        cfg.add_section('some.domain')
        cfg.set('some.domain', 'foo', '1')
        with open(self.filename, 'w') as fd:
            cfg.write(fd)

        config = load_config()
        assert config == {}

        clear_config()

        config = load_config()
        self.assertEqual(config, {})

    def test_clear_config_removes_existing_section(self):
        cfg = ConfigParser()
        cfg.add_section('login.ubuntu.com')
        cfg.set('login.ubuntu.com', 'foo', '1')
        with open(self.filename, 'w') as fd:
            cfg.write(fd)

        config = load_config()
        assert config != {}

        clear_config()

        config = load_config()
        self.assertEqual(config, {})

    def test_clear_config_with_no_existing_file(self):
        config = load_config()
        assert config == {}

        clear_config()

        config = load_config()
        self.assertEqual(config, {})
