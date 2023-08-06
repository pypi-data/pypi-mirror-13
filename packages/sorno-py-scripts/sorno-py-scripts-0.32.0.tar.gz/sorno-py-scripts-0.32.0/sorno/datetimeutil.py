"""datetimeutil converts between different datetime related objects.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import time

import pytz
import re
import tzlocal


ISO_FORMAT= "%Y-%m-%dT%H:%M:%S%z"
ISO_FORMAT_WITH_TZ_NAME = "%Y-%m-%dT%H:%M:%S%z%Z"
# Mon Jan 2 15:04:05 -0700 MST 2006
GO_REFERENCE_TIME = datetime.datetime(
    2006,
    1,
    2,
    15,
    4,
    5,
    tzinfo=pytz.timezone("US/Mountain"),
)

LOCAL_TIMEZONE = tzlocal.get_localzone()
TIMESTAMP_REGEX = re.compile(r"((?<=\D)|^)(\d{10,19})((?=\D)|$)")

_timestamp_units = ["s", "ms", "us", "ns"]


def real_localize(dt, tz):
    """Attach timezone info to a datetime object.

    This is basically tz.normalize(tz.localize(dt))

    Args:
        dt: A datetime.
        tz: A pytz timezone.

    Returns:
        A datetime object which is a clone of the given dt, with the given
        timezone info attached.
    """
    return tz.normalize(tz.localize(dt))


def datetime_to_timestamp(dt):
    """Converts datetime to a UNIX timestamp.

    Args:
        dt: A datetime. The datetime to be converted.

    Returns:
        An integer that represents the converted UNIX timestamp in seconds.
    """
    return time.mktime(dt.timetuple())


def timestamp_to_local_datetime(timestamp):
    """Converts timestamp to a datetime with local timezone info.

    Args:
        timestamp: An int. The UNIX timestamp in seconds to be converted.

    Returns:
        The converted datetime object with local timezone info.
    """
    dt = datetime.datetime.fromtimestamp(timestamp, LOCAL_TIMEZONE)
    return dt


def number_to_local_datetime(number):
    """Guesses the units of a timestamp.

    Args:
        number: An int. The number that is assumed to be a UNIX timestamp
            without units specified.

    Returns:
        A tuple of (datetime, str). The first element is the datetime object
        for the timestamp with local one info. The second element is the guessed
        unit, which can be s, ms, us, or ns. Raise ValueError if a valid
        conversion cannot be done.
    """
    i = 0
    n = number
    while n > 10 ** 10:
        n /= 1000
        i += 1
        if i >= len(_timestamp_units):
            raise ValueError("number %s is too big" % number)

    dt = datetime.datetime.fromtimestamp(n, LOCAL_TIMEZONE)
    return dt, _timestamp_units[i]
