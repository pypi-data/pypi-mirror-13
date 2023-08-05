# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import logging

from click_toolbelt.common import (
    Command,
    CommandError,
)
from storeapi.channels import get_channels, update_channels


class Channels(Command):
    """Get/Update channels configuration for a package."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Channels, self).get_parser(prog_name)
        parser.add_argument('package_name')
        parser.add_argument('config_filename', nargs='?')
        parser.add_argument('--publish', action="store_true")
        return parser

    def get_channels_config(self, config_filename, publish=False):
        """Return config data as expected by channels endpoint."""
        if config_filename:
            with open(config_filename, 'r') as fd:
                data = json.load(fd)
        else:
            data = {}
        config = {'channels': data, 'publish': publish}
        return config

    def show_channels(self, data):
        """Display given channels config."""
        for config in data:
            value = config.get('current')
            if value is not None:
                value = 'Revision %d (version %s)' % (
                    value.get('revision'), value.get('version'))
            self.log.info('%s: %s', config.get('channel'), value)

    def take_action(self, parsed_args):
        package_name = parsed_args.package_name
        config_filename = parsed_args.config_filename
        publish = parsed_args.publish

        # OAuth session is required
        session = self.get_oauth_session()
        if session is None:
            self.log.info('No valid credentials found.')
            # raise an exception to exit with proper code
            raise CommandError()

        if not publish and config_filename is None:
            # no changes requested, ask for current config
            result = get_channels(session, package_name)
        else:
            config = self.get_channels_config(
                config_filename, publish=publish)
            result = update_channels(session, package_name, config)

        if not result.get('success', False):
            self.log.info(
                'Could not get information. An error ocurred:\n\n%s\n\n',
                '\n'.join(result['errors']))
            # raise an exception to exit with proper code
            raise CommandError()

        errors = result.get('errors', [])
        for error in errors:
            self.log.info('ERROR: %s', error)

        data = result['data']
        self.show_channels(data)
