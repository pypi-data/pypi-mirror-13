# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import os

from xdg.BaseDirectory import load_first_config, save_config_path

from click_toolbelt import __namespace__
from click_toolbelt.compat import ConfigParser, urlparse
from click_toolbelt.constants import (
    CLICK_TOOLBELT_PROJECT_NAME,
    UBUNTU_SSO_API_ROOT_URL,
)


def load_config():
    """Read and return configuration from disk."""
    config_dir = load_first_config(CLICK_TOOLBELT_PROJECT_NAME)
    filename = os.path.join(config_dir, "%s.cfg" % __namespace__)
    parser = ConfigParser()
    if os.path.exists(filename):
        parser.read(filename)

    api_endpoint = os.environ.get(
        'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
    location = urlparse(api_endpoint).netloc

    config = {}
    if parser.has_section(location):
        config.update(dict(parser.items(location)))
    return config


def save_config(data):
    """Store current configuration to disk."""
    config_dir = save_config_path(CLICK_TOOLBELT_PROJECT_NAME)

    filename = os.path.join(config_dir, "%s.cfg" % __namespace__)
    parser = ConfigParser()
    if os.path.exists(filename):
        parser.read(filename)

    api_endpoint = os.environ.get(
        'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
    location = urlparse(api_endpoint).netloc
    if not parser.has_section(location):
        parser.add_section(location)

    for key, value in data.items():
        parser.set(location, key, str(value))

    with open(filename, 'w') as fd:
        parser.write(fd)


def clear_config():
    """Remove configuration section from files on disk."""
    config_dir = save_config_path(CLICK_TOOLBELT_PROJECT_NAME)

    filename = os.path.join(config_dir, "%s.cfg" % __namespace__)
    parser = ConfigParser()
    if os.path.exists(filename):
        parser.read(filename)

    api_endpoint = os.environ.get(
        'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
    location = urlparse(api_endpoint).netloc
    parser.remove_section(location)

    with open(filename, 'w') as fd:
        parser.write(fd)
