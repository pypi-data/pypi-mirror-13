from __future__ import unicode_literals, absolute_import

import six


def hasattr_safe(obj, attr_name):
    if six.PY3:
        return hasattr(obj, attr_name)
    else:
        try:
            getattr(obj, attr_name)
        except AttributeError:
            return False
        return True
