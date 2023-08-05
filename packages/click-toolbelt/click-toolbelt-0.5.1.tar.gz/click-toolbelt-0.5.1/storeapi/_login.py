# -*- coding: utf-8 -*-
# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import os

from ssoclient.v2 import (
    ApiException,
    UnexpectedApiError,
    V2ApiClient,
)

from storeapi.constants import (
    UBUNTU_SSO_API_ROOT_URL,
)


def login(email, password, token_name, otp=None):
    """Log in via the Ubuntu One SSO API.

    If successful, returns the oauth token data.
    """
    result = {
        'success': False,
        'body': None,
    }

    api_endpoint = os.environ.get(
        'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
    client = V2ApiClient(endpoint=api_endpoint)
    data = {
        'email': email,
        'password': password,
        'token_name': token_name,
    }
    if otp is not None:
        data['otp'] = otp
    try:
        response = client.login(data=data)
        result['body'] = response
        result['success'] = True
    except ApiException as err:
        result['body'] = err.body
    except UnexpectedApiError as err:
        result['body'] = err.json_body
    return result
