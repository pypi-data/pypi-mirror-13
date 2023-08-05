# coding: utf-8
import pytest


value_expected = lambda *values: pytest.mark.parametrize('value, expected', values)
first_second_expected = lambda *values: pytest.mark.parametrize('first, second, expected', values)
binary_operation = lambda *values: pytest.mark.parametrize('first, second, expected, operation', values)
