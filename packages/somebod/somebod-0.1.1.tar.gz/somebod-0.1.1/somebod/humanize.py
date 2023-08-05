# -*- coding: UTF-8 -*-

import decimal
import six

intword_converters = ((1E15, "P"), (1E12, "T"), (1E9, "G"), (1E6, "M"), (1E3, "K"))
duration_suffixes = dict((("s", 1), ("m", 60), ("h", 60 * 60), ("d", 24 * 60 * 60),
                         ("w", 7 * 24 * 60 * 60), ("y", 365 * 7 * 24 * 60 * 60)))


def intword(val):
    """
      Converts a large number to a friendly text representation.
      Inspired in large part by django.contrib.humanize
    """
    if val is None:
        return ""
    if isinstance(val, six.string_types):
        return val

    if isinstance(val, decimal.Decimal):
        val = float(val)

    for thr, suffix in intword_converters:
        if val > thr:
            return "%.1f%s" % (float(val) / thr, suffix)
    if isinstance(val, float):
        return "%.1f" % val
    return str(val)


def print_ratio(value, den):
    """
        Human output of a ratio
    """
    return "%s/%s (%.2f%%)" % (intword(value), intword(den), 100. * value / den if den else 0.)


def parse_duration(duration):
    """
        Parse human duration into duration in seconds
    """
    if not isinstance(duration, six.string_types):
        raise TypeError("Cannot parse duration. Must be string or unicode")
    if duration.isdigit():
        return int(duration)
    suffix = duration[-1]
    prefix = duration[:-1]
    return int(prefix) * duration_suffixes[suffix]
