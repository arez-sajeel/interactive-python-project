from decimal import Decimal

from calc import basket_total


def test_discount_applied_at_40_or_more():
    assert basket_total([(12.50, 2), (8.00, 1), (5.50, 2)]) == Decimal("39.60")


def test_discount_applied_at_exactly_40():
    assert basket_total([(20.00, 2)]) == Decimal("36.00")


def test_no_discount_under_40():
    assert basket_total([(5.00, 3)]) == Decimal("15.00")
