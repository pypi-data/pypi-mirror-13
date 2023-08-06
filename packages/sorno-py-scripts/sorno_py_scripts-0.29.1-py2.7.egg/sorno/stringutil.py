"""
Utility functions for dealing with strings
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re


def oneline(s):
    """
    Compact all space characters to a single space. Leading and trailing
    spaces are stripped.
    """
    return re.sub(r"\s+", " ", s).strip()


def u(s):
    """
    Converts s to unicode with utf-8 encoding if it is not already a unicode.
    Leave it as is otherwise.
    """
    if type(s) == unicode:
        return s
    else:
        return s.decode("utf8")
