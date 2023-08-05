from __future__ import unicode_literals, absolute_import

import sys

from .hasattr_safe import hasattr_safe

sys.modules[__name__] = hasattr_safe
