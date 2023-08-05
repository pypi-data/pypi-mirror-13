# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import time
from functools import wraps

import cliff.command

from click_toolbelt.config import clear_config, load_config, save_config


class CommandError(Exception):
    """Exception to mark command errored out."""


class Command(cliff.command.Command):

    def load_config(self):
        """Read and return configuration from disk."""
        return load_config()

    def save_config(self, data):
        """Store current configuration to disk."""
        save_config(data)

    def clear_config(self):
        """Remove remove configuration section from files on disk."""
        clear_config()

    def get_oauth_session(self):
        """Return a client configured to allow oauth signed requests."""
        # import here to avoid circular import
        from click_toolbelt.api.common import get_oauth_session
        return get_oauth_session()

    def take_action(self, parsed_args):
        pass  # pragma: no cover


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
