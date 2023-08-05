# -*- coding: utf-8 -*-
# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import logging

from click_toolbelt.common import (
    Command,
    CommandError,
)
from click_toolbelt.constants import (
    CLICK_TOOLBELT_PROJECT_NAME,
)
from storeapi import login


class Login(Command):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Login, self).get_parser(prog_name)
        parser.add_argument('email')
        parser.add_argument('password')
        parser.add_argument('otp', nargs='?')
        return parser

    def take_action(self, parsed_args):
        login_data = {
            'email': parsed_args.email,
            'password': parsed_args.password,
            'token_name': CLICK_TOOLBELT_PROJECT_NAME,
        }
        if parsed_args.otp:
            login_data['otp'] = parsed_args.otp

        response = login(**login_data)
        if response.get('success', False):
            self.log.info('Login successful.')
            self.save_config(response['body'])
        else:
            error = response['body']
            self.log.info(
                'Login failed.\n'
                'Reason: %s\n'
                'Detail: %s',
                error['code'], error['message'])
            # raise an exception to exit with proper code
            raise CommandError()
