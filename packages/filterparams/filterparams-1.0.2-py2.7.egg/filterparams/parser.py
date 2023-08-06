# -*- encoding: utf-8 -*-

from __future__ import absolute_import
import re

from .binding import loads
from .obj import (
    Query,
    Parameter,
    And,
    Order,
)
from .util import to_multidict


FILTER_DETECTOR = re.compile(
    ur'^filter\[param\]'
    ur'\[(?P<name>\w+)\]'
    ur'(?:\[(?P<filter_name>\w+)\]'
    ur'(?:\[(?P<alias>\w+)\])?)?$',
    re.IGNORECASE,
)
ORDER_KEY = u'filter[order]'
ORDER_PARAM_FILTER = re.compile(
        ur'^(?:'
        ur'(?P<sort_order>desc|asc)\((?P<order_param>\w+)\)'
        ur'|'
        ur'(?P<unsorted_order_param>\w+)'
        ur')$'
)
FILTER_BINDING_KEY = u'filter[binding]'


class Parser(object):

    def __init__(self, query_dict, **kwargs):
        self._query_dict = query_dict
        self.default_filter = kwargs.get(u'default_filter')

    @property
    def _query_dict(self):
        return self._safe_multi_dict

    @_query_dict.setter
    def _query_dict(self, value):
        self._safe_multi_dict = to_multidict(value)

    @property
    def query(self):
        query = Query()
        for param in self._params:
            query.add_param(param)
        for order in self._orders:
            query.add_order(order)
        query.param_order = self._param_ordering(query)

        return query

    @property
    def _params(self):
        for key in self._query_dict.keys():
            param_obj = self._generate_param_if_valid(key)
            if param_obj is not None:
                yield param_obj

    def _generate_param_if_valid(self, param_key):
        matcher = FILTER_DETECTOR.match(param_key)
        if matcher is None:
            return None
        name = matcher.group(u'name')
        filter_name = (
            matcher.group(u'filter_name') or
            self.default_filter
        )
        alias = matcher.group(u'alias') or name
        return Parameter(
            name=name,
            filter=filter_name,
            alias=alias,
            value=self._query_dict.get(param_key),
        )

    @property
    def _orders(self):
        for order in self._query_dict.getlist(ORDER_KEY):
            order_item = self._generate_order(order)
            if order_item is not None:
                yield order_item

    @staticmethod
    def _generate_order(order_item):
        order_match = ORDER_PARAM_FILTER.match(order_item)
        if order_match is None:
            return
        sort_order = order_match.group(u'sort_order')
        order_param = (
            order_match.group(u'order_param') or
            order_match.group(u'unsorted_order_param')
        )
        return Order(order_param, sort_order)

    def _param_ordering(self, query):
        if FILTER_BINDING_KEY in self._query_dict:
            binding, _ = loads(
                self._query_dict.get(FILTER_BINDING_KEY),
                query
            )
            return binding
        else:
            return self._default_param_ordering(query)

    def _default_param_ordering(self, query):
        binding = None
        for param in query.params:
            if binding is None:
                binding = param
            else:
                binding = And(binding, param)
        return binding

