import pytest

from demo_math import add, divide, multiply, subtract


def test_adds_two_numbers() -> None:
    assert add(2, 3) == 5


def test_subtracts_two_numbers() -> None:
    assert subtract(8, 3) == 5


def test_multiplies_two_numbers() -> None:
    assert multiply(4, 3) == 12


def test_divides_two_numbers() -> None:
    assert divide(8, 2) == 4


def test_divide_by_zero_raises_error() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)

