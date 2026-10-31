import pytest

from calc import basket_total


def test_discount_applied_over_40():
    assert basket_total([(12.50, 2), (5.00, 4)]) == pytest.approx(40.50)


def test_no_discount_under_40():
    assert basket_total([(5.00, 3)]) == pytest.approx(15.00)
