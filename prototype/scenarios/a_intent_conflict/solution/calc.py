from decimal import Decimal


def basket_total(items):
    """Calculate the basket total, applying 10% off at £40 or more."""
    subtotal = sum(
        Decimal(str(price)) * quantity
        for price, quantity in items
    )

    if subtotal >= Decimal("40"):
        subtotal *= Decimal("0.90")

    return subtotal


def format_price(price):
    """Format a price as pounds and pence."""
    return f"£{price:.2f}"
