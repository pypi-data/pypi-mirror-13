# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from sqlalchemy import String

from .util import convert, is_type


class Filter(object):
    name = None

    def __init__(self, converters):
        self.converters = converters

    def __eq__(self, other):
        if isinstance(other, Filter):
            return other.name == self.name
        elif isinstance(other, unicode):
            return self.name == other
        else:
            super(Filter, self).__eq__(other)

    def __call__(self, param, value):
        return self.apply(param, value)

    def apply(self, param, value):
        if hasattr(param, u'type'):
            type_cl = param.type
        else:
            type_cl = param
        value = self._convert(type_cl, value)
        return self._apply(param, value)

    def _convert(self, type_cl, value):
        return convert(value, type_cl, self.converters)


class EqFilter(Filter):
    name = u'eq'

    def _apply(self, param, value):
        return param == value


class NeqFilter(Filter):
    name = u'neq'

    def _apply(self, param, value):
        return param != value


class LesserFilter(Filter):
    name = u'lt'

    def _apply(self, param, value):
        return param < value


class LesserEqualFilter(Filter):
    name = u'lte'

    def _apply(self, param, value):
        return param <= value


class GreaterFilter(Filter):
    name = u'gt'

    def _apply(self, param, value):
        return param > value


class GreaterEqualFilter(Filter):
    name = u'gte'

    def _apply(self, param, value):
        return param >= value


class _LikeBase(Filter):
    def apply(self, param, value):
        if not is_type(param.type, String):
            raise ValueError(
                u'Like is only possible on string'
            )
        return super(_LikeBase, self).apply(param, value)


class LikeFilter(_LikeBase):
    name = u'like'

    def _apply(self, param, value):
        return param.like(value)


class ILikeFilter(_LikeBase):
    name = u'ilike'

    def _apply(self, param, value):
        return param.ilike(value)


DEFAULT_FILTERS = [
    EqFilter,
    NeqFilter,
    LesserFilter,
    LesserEqualFilter,
    GreaterFilter,
    GreaterEqualFilter,
    LikeFilter,
    ILikeFilter,
]

