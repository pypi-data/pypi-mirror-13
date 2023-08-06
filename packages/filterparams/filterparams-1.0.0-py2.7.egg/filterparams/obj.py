# -*- encoding: utf-8 -*-


class Query(object):
    def __init__(self):
        self._parameters = {}
        self._aliased_parameters = {}
        self.param_order = None
        self.orders = []

    def add(self, name, **kwargs):
        return self.add_param(
                Parameter(
                        name=name,
                        **kwargs
                )
        )

    @property
    def params(self):
        return self._parameters.values()

    def add_param(self, parameter):
        self._parameters[parameter.name] = parameter
        self._aliased_parameters[parameter.alias] = parameter

    def has_param(self, name):
        return name in self._parameters

    def get_param(self, name):
        return self._parameters[name]

    def get_aliased_param(self, name):
        return self._aliased_parameters[name]

    def has_param_with_alias(self, name):
        return name in self._aliased_parameters

    def add_order(self, order):
        self.orders.append(order)


class Parameter(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.filter = kwargs.get(u'filter', None)
        self.value = kwargs.get(u'value', None)
        self.alias = kwargs.get(u'alias', name)

    def __eq__(self, other):
        other = getattr(other, u'name', other)
        return other == self.name


class Order(object):
    def __init__(self, param, direction=None):
        self.name = param
        self.direction = direction

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if value not in (u'asc', u'desc'):
            value = u'asc'
        self._direction = value


class BindingOperation(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (
            self.left == other.left and
            self.right == other.right
        )


class And(BindingOperation):
    def __eq__(self, other):
        if not isinstance(other, And):
            return False
        return super(And, self).__eq__(other)


class Or(BindingOperation):
    def __eq__(self, other):
        if not isinstance(other, Or):
            return False
        return super(Or, self).__eq__(other)


class Not(object):
    def __init__(self, inner):
        self.inner = inner

    def __eq__(self, other):
        if not isinstance(other, Not):
            return False
        return self.inner == other.inner

