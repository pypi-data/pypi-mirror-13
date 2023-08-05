# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals

import cliff.command

from click_toolbelt.config import clear_config, load_config, save_config
from storeapi.common import get_oauth_session


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
        config = load_config()
        return get_oauth_session(config)

    def take_action(self, parsed_args):
        pass  # pragma: no cover
