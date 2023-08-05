# -*- coding: utf-8 -*-

from functools import wraps
import inspect
import types
import uuid
import math
import re
import sys
from datetime import datetime
from keystone.py3compat import iteritems, string_types

# timestamp formats
ISO8601 = "%Y-%m-%dT%H:%M:%S.%f"
ISO8601_PAT = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d{1,6})?Z?([\+\-]\d{2}:?\d{2})?$")

# holy crap, strptime is not threadsafe.
# Calling it once at import seems to help.
datetime.strptime("1", "%d")

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------


def parse_date(s):
    """parse an ISO8601 date string

    If it is None or not a valid ISO8601 timestamp,
    it will be returned unmodified.
    Otherwise, it will return a datetime object.
    """
    if s is None:
        return s
    m = ISO8601_PAT.match(s)
    if m:
        # FIXME: add actual timezone support
        # this just drops the timezone info
        notz, ms, tz = m.groups()
        if not ms:
            ms = '.0'
        notz = notz + ms
        return datetime.strptime(notz, ISO8601)
    return s


def extract_dates(obj):
    """extract ISO8601 dates from unpacked JSON"""
    if isinstance(obj, dict):
        new_obj = {}  # don't clobber
        for k, v in iteritems(obj):
            new_obj[k] = extract_dates(v)
        obj = new_obj
    elif isinstance(obj, (list, tuple)):
        obj = [extract_dates(o) for o in obj]
    elif isinstance(obj, string_types):
        obj = parse_date(obj)
    return obj


def squash_dates(obj):
    """squash datetime objects into ISO8601 strings"""
    if isinstance(obj, dict):
        obj = dict(obj)  # don't clobber
        for k, v in iteritems(obj):
            obj[k] = squash_dates(v)
    elif isinstance(obj, (list, tuple)):
        obj = [squash_dates(o) for o in obj]
    elif isinstance(obj, datetime):
        obj = obj.isoformat()
    return obj


def date_default(obj):
    """default function for packing datetime objects in JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        raise TypeError("%r is not JSON serializable" % obj)


def tolerant_equals(a, b, atol=10e-7, rtol=10e-7):
    return math.fabs(a - b) <= (atol + rtol * math.fabs(b))


def isint(num):
    return isinstance(num, int)


def isnumber(num):
    return isinstance(num, (int, float))


def get_caller_name(skip=2):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename)  # function or a method
    del parentframe
    return name


def generate_uuid():
    return uuid.uuid4().hex
