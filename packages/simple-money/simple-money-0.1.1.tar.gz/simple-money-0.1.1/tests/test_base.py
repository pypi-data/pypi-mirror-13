# coding: utf-8
import sys
from decimal import Decimal
from operator import *

import pytest

from .conftest import value_expected, first_second_expected, binary_operation
from simple_money import Money


if sys.version > '3':
    unicode = str
    div = truediv


def test_base_attributes():
    amount, currency = 100, 'EUR'
    money = Money(amount, currency)
    assert money.amount == amount
    assert money.currency == currency


@pytest.mark.parametrize('amount', (100, '100', '100.0', 13.45, Decimal(100)))
def test_amount_always_decimal(amount):
    assert isinstance(Money(amount).amount, Decimal)


@value_expected(((1, 'EUR'), '1 EUR'))
def test_string_representation(value, expected):
    money = Money(*value)
    assert str(money) == unicode(money) == repr(money) == expected


@pytest.mark.parametrize(
    'value, expected, operation',
    (
        (1, 1, pos), (1., 1., pos), (Decimal(1), Decimal(1), pos), (-1, -1, pos),
        (1, -1, neg), (1., -1., neg), (Decimal(1), Decimal(-1), neg), (-1, 1, neg)
    )
)
def test_unary_operation(value, expected, operation):
    assert operation(Money(value)) == Money(expected)


@first_second_expected((100, 100, 200), (0, 0, 0), (-1, -1, -2), (100, Money(50), 150))
def test_addition(first, second, expected):
    assert second + Money(first) == Money(expected)
    assert Money(first) + second == Money(expected)


@first_second_expected((100, 100, 0), (0, 0, 0), (-1, -1, 0), (100, 50, -50))
def test_right_subtraction(first, second, expected):
    first, expected = Money(first), Money(expected)
    assert second - first == expected
    assert Money(second) - first == expected


@first_second_expected((100, 100, 0), (0, 0, 0), (-1, -1, 0), (100, 50, 50))
def test_left_subtraction(first, second, expected):
    first, expected = Money(first), Money(expected)
    assert first - second == expected
    assert first - Money(second) == expected


@value_expected(((100, 100), 200), ((100, -100), 0), ((0., 1), 1))
def test_sum(value, expected):
    assert sum([Money(amount) for amount in value]) == Money(expected)


@binary_operation(
    (100, 100, 200, add), (0, 0, 0, add), (-1, -1, -2, add),
    (100, 100, 0, sub), (0, 0, 0, sub), (-1, -1, 0, sub),
    (100, 3, 300, mul), (0, 0, 0, mul), (-1, -1., 1, mul),
    (100, 8, 12.5, div), (1, 1, 1, div), (-1, -1., 1, div),
    (100, 8, 12, floordiv), (1, 2, 0, floordiv), (-10, -3., 3, floordiv)
)
def test_binary_operations(first, second, expected, operation):
    result = operation(Money(first), second)
    assert result == Money(expected)
    assert isinstance(result.amount, Decimal)


@binary_operation(
    (1, 1, True, eq), (1., 1., True, eq), (Decimal(1), Decimal(1), True, eq), (-1, -1, True, eq),
    (1, 1, False, lt), (1, 0, False, lt), (1, 2, True, lt),
    (1, 1, True, le), (1, 0, False, le), (1, 2, True, le),
    (1, 1, False, gt), (1, 0, True, gt), (1, 2, False, gt),
    (1, 1, True, ge), (1, 0, True, ge), (1, 2, False, ge)
)
def test_binary_operations_with_boolean_results(first, second, expected, operation):
    assert operation(Money(first), Money(second)) == expected


def test_rmul():
    assert (2 * Money(100, 'EUR')).amount == 200
