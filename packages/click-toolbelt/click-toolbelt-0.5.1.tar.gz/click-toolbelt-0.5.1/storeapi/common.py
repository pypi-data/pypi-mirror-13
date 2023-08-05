# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
import json
import os
import time
from functools import wraps

import requests
from requests_oauthlib import OAuth1Session

from storeapi.compat import urljoin
from storeapi.constants import MYAPPS_API_ROOT_URL


def get_oauth_session(config):
    """Return a client configured to allow oauth signed requests."""
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


def is_scan_completed(response):
    """Return True if the response indicates the scan process completed."""
    if response.ok:
        return response.json().get('completed', False)
    return False


def retry(terminator=None, retries=3, delay=3, backoff=2, logger=None):
    """Decorate a function to automatically retry calling it on failure.

    Arguments:
        - terminator: this should be a callable that returns a boolean;
          it is used to determine if the function call was successful
          and the retry loop should be stopped
        - retries: an integer specifying the maximum number of retries
        - delay: initial number of seconds to wait for the first retry
        - backoff: exponential factor to use to adapt the delay between
          subsequent retries
        - logger: logging.Logger instance to use for logging

    The decorated function will return as soon as any of the following
    conditions are met:

        1. terminator evaluates function output as True
        2. there are no more retries left

    If the terminator callable is not provided, the function will be called
    exactly once and will not be retried.

    """
    def decorated(func):
        if retries != int(retries) or retries < 0:
            raise ValueError(
                'retries value must be a positive integer or zero')
        if delay < 0:
            raise ValueError('delay value must be positive')

        if backoff != int(backoff) or backoff < 1:
            raise ValueError('backoff value must be a positive integer')

        @wraps(func)
        def wrapped(*args, **kwargs):
            retries_left, current_delay = retries, delay

            result = func(*args, **kwargs)
            if terminator is not None:
                while not terminator(result) and retries_left > 0:
                    msg = "... retrying in %d seconds" % current_delay
                    if logger:
                        logger.warning(msg)

                    # sleep
                    time.sleep(current_delay)
                    retries_left -= 1
                    current_delay *= backoff

                    # retry
                    result = func(*args, **kwargs)
            return result, retries_left == 0

        return wrapped
    return decorated
