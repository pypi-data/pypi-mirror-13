# coding: utf-8

import datetime

from .duration import to_str


def timedetla_to_str(value):
    if isinstance(value, datetime.timedelta):
        return to_str(value)
    return value
