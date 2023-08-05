# -*- coding: utf-8 -*-
# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals

from storeapi.common import myapps_api_call


def get_channels(session, package_name):
    """Get current channels config for package through API."""
    channels_endpoint = 'package-channels/%s/' % package_name
    return myapps_api_call(channels_endpoint, session=session)


def update_channels(session, package_name, data):
    """Update current channels config for package through API."""
    channels_endpoint = 'package-channels/%s/' % package_name
    result = myapps_api_call(channels_endpoint, method='POST',
                             data=data, session=session)
    if result['success']:
        result['errors'] = result['data']['errors']
        result['data'] = result['data']['channels']
    return result
