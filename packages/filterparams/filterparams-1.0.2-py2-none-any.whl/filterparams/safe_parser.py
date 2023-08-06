# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from .parser import Parser


class SafeParser(Parser):
    u"""
    Usual parser which also verifies the
    supported operations.
    """

    def __init__(self, query_dict, valid_filters, **kwargs):
        super(SafeParser, self).__init__(query_dict, **kwargs)
        self.filters = valid_filters

    @property
    def _params(self):
        for param in super(SafeParser, self)._params:
            self._verify_filter_of(param)
            yield param

    def _verify_filter_of(self, parameter):
        if parameter.filter not in self.filters:
            raise ValueError(
                (
                    u'The filter {filter} of '
                    u'parameter {name} with alias'
                    u'{alias} is unknown'
                ).format(
                    name=parameter.name,
                    alias=parameter.alias,
                    filter=parameter.filter,
                )
            )

