# -*- encoding: utf-8 -*-

from __future__ import absolute_import
import itertools

from werkzeug.datastructures import MultiDict
from itertools import izip


def to_multidict(value):
    if not isinstance(value, MultiDict) and isinstance(value, dict):
        value = _dict_to_multidict(value)
    return value


def create_key_value_pairs(dictionary, key):
    if hasattr(dictionary, u'getall'):
        get_values = lambda key: dictionary.getall(key)
    else:
        get_values = lambda key: [dictionary.get(key)]

    values = get_values(key)
    return izip([key] * len(values), values)


def _dict_to_multidict(value):
    return MultiDict(
        itertools.chain.from_iterable(
            create_key_value_pairs(value, key)
            for key in value.keys()
        )
    )

