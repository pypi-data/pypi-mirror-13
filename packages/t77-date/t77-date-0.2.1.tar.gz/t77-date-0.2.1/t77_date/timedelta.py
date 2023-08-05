"""datetime.timedelta related functions"""
from __future__ import absolute_import
from datetime import timedelta

from .constants import MICROSECONDS_IN_SECOND, SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE, HOURS_IN_DAY


def timedelta_to_seconds(val, with_microseconds=False):
    """
    Convert datetime.timedelta to seconds
    :param val: timedelta to convert
    :type val: datetime.timedelta
    :param with_microseconds:
    :type with_microseconds: bool
    :return: seconds/seconds with microseconds or None if val is None
    :rtype: int/float/None
    :raise: TypeError when val is not timedelta
    """
    if val is None:
        return None

    if type(val) != timedelta:
        raise TypeError('')

    microseconds = with_microseconds and 1.0 * val.microseconds / MICROSECONDS_IN_SECOND or 0

    return val.days * SECONDS_IN_DAY + val.seconds + microseconds


def timedelta_to_str(val, with_microseconds=False):
    """
    String representation of datetime.timedelta
    :param val: timedelta to convert
    :type val: datetime.timedelta
    :param with_microseconds:
    :type with_microseconds: bool
    :return: String representation of datetime.timedelta or None if val is None
    :rtype: string/None
    :raise: TypeError when val is not timedelta
    """
    if val is None:
        return None

    if type(val) != timedelta:
        raise TypeError('')

    hours, remainder = divmod(val.seconds, SECONDS_IN_HOUR)
    hours += val.days * HOURS_IN_DAY
    minutes, seconds = divmod(remainder, SECONDS_IN_MINUTE)

    if with_microseconds:
        return '%02d:%02d:%02d.%06d' % (hours, minutes, seconds, val.microseconds)
    else:
        return '%02d:%02d:%02d' % (hours, minutes, seconds)
