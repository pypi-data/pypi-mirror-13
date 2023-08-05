# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import logging

from click_toolbelt.common import (
    Command,
    CommandError,
)
from storeapi import upload


class Upload(Command):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Upload, self).get_parser(prog_name)

        parser.add_argument('binary_filename')
        metadata_group = parser.add_mutually_exclusive_group()
        metadata_group.add_argument('metadata_filename', nargs='?')
        metadata_group.add_argument('--metadata', metavar='metadata_filename',
                                    dest='metadata_filename')

        return parser

    def take_action(self, parsed_args):
        self.log.info('Running scan-upload command...')

        binary_filename = parsed_args.binary_filename
        metadata_filename = parsed_args.metadata_filename

        success = upload(binary_filename, metadata_filename)
        if not success:
            # raise an exception to exit with proper code
            raise CommandError()
