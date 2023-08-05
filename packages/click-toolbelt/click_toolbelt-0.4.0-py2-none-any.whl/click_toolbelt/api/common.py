# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
import json
import os

import requests
from requests_oauthlib import OAuth1Session

from click_toolbelt.compat import urljoin
from click_toolbelt.config import load_config
from click_toolbelt.constants import MYAPPS_API_ROOT_URL


def get_oauth_session():
    """Return a client configured to allow oauth signed requests."""
    config = load_config()
    try:
        session = OAuth1Session(
            config['consumer_key'],
            client_secret=config['consumer_secret'],
            resource_owner_key=config['token_key'],
            resource_owner_secret=config['token_secret'],
            signature_method='PLAINTEXT',
        )
    except KeyError:
        session = None
    return session


def myapps_api_call(path, session=None, method='GET', data=None):
    """Issue a request for a particular endpoint of the MyApps API."""
    result = {'success': False, 'errors': [], 'data': None}
    if session is not None:
        client = session
    else:
        client = requests

    root_url = os.environ.get('MYAPPS_API_ROOT_URL', MYAPPS_API_ROOT_URL)
    url = urljoin(root_url, path)
    if method == 'GET':
        response = client.get(url)
    elif method == 'POST':
        response = client.post(url, data=data and json.dumps(data) or None,
                               headers={'Content-Type': 'application/json'})
    else:
        raise ValueError('Method {} not supported'.format(method))

    if response.ok:
        result['success'] = True
        result['data'] = response.json()
    else:
        result['errors'] = [response.text]
    return result
