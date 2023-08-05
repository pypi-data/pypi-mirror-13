# -*- coding: utf-8 -*-
# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals

from storeapi.common import myapps_api_call


def get_info():
    """Return information about the MyApps API.

    Returned data contains information about:
    - version
    - department
    - license
    - country
    - channel
    """
    return myapps_api_call('')
