# coding: utf-8
import pytest

from simple_money import Money, CompoundMoney


eur, usd = Money(100, 'EUR'), Money(100, 'USD')
compound = CompoundMoney(usd, eur, usd)


def test_pool():
    assert compound.USD.amount == 200
    assert compound.USD.currency == 'USD'
    assert compound.EUR.amount == 100
    assert compound.EUR.currency == 'EUR'


def test_pool_exception():
    with pytest.raises(AttributeError):
        assert compound.CZK


def test_repr():
    assert str(compound) == '100 EUR, 200 USD'


def test_neg():
    result = -compound
    assert result.EUR.amount == -100
    assert result.USD.amount == -200


def test_negative_repr():
    result = Money(100, 'EUR') - Money(150, 'USD')
    assert str(result) == '100 EUR, -150 USD'


class TestCompound:

    def test_equality(self):
        assert compound == compound
        assert compound == (Money(100, 'EUR') + Money(200, 'USD'))

    def test_pos(self):
        result = +compound
        assert compound == result

    def test_addition(self):
        result = compound + compound
        assert result.EUR.amount == 200
        assert result.USD.amount == 400

    def test_subtraction(self):
        result = compound - (Money(55, 'EUR') + Money(10, 'USD'))
        assert result.EUR.amount == 45
        assert result.USD.amount == 190

    def test_multiplication(self):
        result = compound * 2
        assert result.EUR.amount == 200
        assert result.USD.amount == 400

    def test_right_multiplication(self):
        result = 2 * compound
        assert result.EUR.amount == 200
        assert result.USD.amount == 400

    def test_division(self):
        result = compound / 2
        assert result.EUR.amount == 50
        assert result.USD.amount == 100

    def test_floor_division(self):
        result = compound // 2
        assert result.EUR.amount == 50
        assert result.USD.amount == 100


class TestMoneyWithCompound:
    """
    Compound money can interact with Money instances in all arithmetic operations.
    """
    money = Money(50, 'EUR')

    def test_subtraction(self):
        result = self.money - compound
        assert result.EUR.amount == -50
        assert result.USD.amount == -200

    def test_right_subtraction(self):
        result = compound - self.money
        assert result.EUR.amount == 50
        assert result.USD.amount == 200

    def test_addition(self):
        result = self.money + compound
        assert result.EUR.amount == 150

    def test_right_addition(self):
        result = compound + self.money
        assert result.EUR.amount == 150
