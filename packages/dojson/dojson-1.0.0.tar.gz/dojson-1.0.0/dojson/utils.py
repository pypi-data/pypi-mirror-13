# -*- coding: utf-8 -*-
#
# This file is part of DoJSON
# Copyright (C) 2015 CERN.
#
# DoJSON is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""Utility functions."""

import codecs
import functools
import json

import six

from .errors import IgnoreKey


def ignore_value(f):
    """Remove key for None value.

    .. versionadded:: 0.2.0

    """
    @functools.wraps(f)
    def wrapper(self, key, value, **kwargs):
        result = f(self, key, value, **kwargs)
        if result is None:
            raise IgnoreKey(key)
        return result
    return wrapper


def filter_values(f):
    """Remove None values from dictionary."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        out = f(*args, **kwargs)
        return dict((k, v) for k, v in six.iteritems(out) if v is not None)
    return wrapper


def for_each_value(f):
    """Apply function to each item."""
    # Extends values under same name in output.  This should be possible
    # because we are alredy expecting list.
    setattr(f, '__extend__', True)

    @functools.wraps(f)
    def wrapper(self, key, values, **kwargs):
        if isinstance(values, (list, tuple, set)):
            return [f(self, key, value, **kwargs) for value in values]
        return [f(self, key, values, **kwargs)]
    return wrapper


def reverse_for_each_value(f):
    """Undo what `for_each_value` does."""
    @functools.wraps(f)
    def wrapper(self, key, values, **kwargs):
        if isinstance(values, (list, tuple, set)):
            if len(values) == 1:
                return f(self, key, values[0], **kwargs)
            return [f(self, key, value, **kwargs) for value in values]

    return wrapper


def force_list(data):
    """Wrap data in list."""
    if data is not None and not isinstance(data, (list, tuple, set)):
        return (data,)
    return data


def reverse_force_list(data):
    """Unwrap data from list if its length is == 1."""
    if isinstance(data, (list, set)) and len(data) == 1:
        return data[0]
    return data


def load(stream):
    """Load JSON from bytestream."""
    reader = codecs.getreader("utf-8")
    return json.load(reader(stream))
