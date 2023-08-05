# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals


try:  # pragma: no cover
    from builtins import open  # noqa
    from configparser import ConfigParser  # noqa
    from urllib.parse import quote_plus, urljoin, urlparse
except ImportError:  # pragma: no cover
    from __builtin__ import open  # noqa
    from ConfigParser import ConfigParser  # noqa
    from urllib import quote_plus  # noqa
    from urlparse import urljoin, urlparse  # noqa
