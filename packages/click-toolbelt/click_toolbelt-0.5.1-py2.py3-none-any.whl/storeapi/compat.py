# Copyright 2015 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals


try:  # pragma: no cover
    from builtins import open  # noqa
    from urllib.parse import quote_plus, urljoin
except ImportError:  # pragma: no cover
    from __builtin__ import open  # noqa
    from urllib import quote_plus  # noqa
    from urlparse import urljoin  # noqa
