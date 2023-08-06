"""dictutil provides additional classes or functions for python dicts
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

class DefaultDictWithEnhancedFactory(defaultdict):
    """Just like the standard python collections.dict,
    but the default_factory takes the missing key as argument.

    Args:
        default_factory: A function that takes the missing key as the argument
        and return a value for the missing key.
        *a: arguments passing to the defaultdict constructor
        **kw: keyword arguments passing to the defaultdict constructor
    """
    def __init__(self, default_factory, *a, **kw):
        defaultdict.__init__(self, default_factory, *a, **kw)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            # Normally, you would expect this line to be
            # called for missing keys...
            return self.default_factory(key)
        except TypeError as ex:
            # However, this is actually getting called
            # because for some reason, defaultdict still
            # intercepts the __getitem__ call and raises:
            # TypeError: <lambda>() takes exactly 1 argument (0 given)
            # So we have to catch that instead...
            if "lambda" in str(ex):
                return self.default_factory(key)
