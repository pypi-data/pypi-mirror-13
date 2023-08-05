# coding: utf-8
from __future__ import division

from decimal import Decimal


class Money(object):

    def __init__(self, amount, currency=None):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return str(self.amount) + ' ' + str(self.currency)

    def __pos__(self):
        return Money(self.amount, self.currency)

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def __eq__(self, other):
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other):
        if isinstance(other, Money):
            other = other.amount
        return self.amount < other

    def __le__(self, other):
        if isinstance(other, Money):
            other = other.amount
        return self.amount <= other

    def __gt__(self, other):
        if isinstance(other, Money):
            other = other.amount
        return self.amount > other

    def __ge__(self, other):
        if isinstance(other, Money):
            other = other.amount
        return self.amount >= other

    def __add__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                return CompoundMoney(self, other)
            other = other.amount
        elif isinstance(other, CompoundMoney):
            return CompoundMoney(self, *other.pool.values())
        return Money(self.amount + other, self.currency)

    def __sub__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                return CompoundMoney(self, -other)
            other = other.amount
        elif isinstance(other, CompoundMoney):
            return CompoundMoney(self, *(-other).pool.values())
        return Money(self.amount - other, self.currency)

    def __rsub__(self, other):
        if isinstance(other, CompoundMoney):
            return CompoundMoney(-self, *other.pool.values())
        return Money(other - self.amount, self.currency)

    def __mul__(self, other):
        return Money(self.amount * Decimal(str(other)), self.currency)

    def __truediv__(self, other):
        return Money(self.amount / Decimal(str(other)), self.currency)

    def __floordiv__(self, other):
        return Money(self.amount // Decimal(str(other)), self.currency)

    __repr__ = __str__
    __radd__ = __add__
    __rmul__ = __mul__
    __div__ = __truediv__


class CompoundMoney(object):

    def __init__(self, *args):
        self.pool = {}
        for value in args:
            self.pool.setdefault(value.currency, Money(0, value.currency))
            self.pool[value.currency] += value

    def __getattribute__(self, item):
        try:
            return super(CompoundMoney, self).__getattribute__(item)
        except AttributeError as exc:
            value = self.pool.get(item)
            if not value:
                raise exc
            return value

    def __str__(self):
        return ', '.join(str(value) for value in sorted(self.pool.values(), key=lambda x: x.currency))

    def __eq__(self, other):
        return self.pool == other.pool

    def __pos__(self):
        return CompoundMoney(*list(self.pool.values()))

    def __neg__(self):
        return CompoundMoney(*[-value for value in self.pool.values()])

    def __add__(self, other):
        values = list(self.pool.values())
        if isinstance(other, Money):
            values += [other]
        else:
            values += list(other.pool.values())
        return CompoundMoney(*values)

    def __sub__(self, other):
        values = list(self.pool.values())
        if isinstance(other, Money):
            values += [-other]
        else:
            values += [-value for value in other.pool.values()]
        return CompoundMoney(*values)

    def __mul__(self, other):
        return CompoundMoney(*[other * value for value in self.pool.values()])

    def __truediv__(self, other):
        return CompoundMoney(*[value / other for value in self.pool.values()])

    def __floordiv__(self, other):
        return CompoundMoney(*[value // other for value in self.pool.values()])

    __repr__ = __str__
    __rmul__ = __mul__
    __div__ = __truediv__
