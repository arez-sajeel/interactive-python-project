def line_total(price, quantity):
    return price * quantity


def apply_discount(subtotal, rate):
    discount = subtotal * rate
    return subtotal + discount


def basket_total(items):
    subtotal = sum(line_total(price, quantity) for price, quantity in items)
    rate = 0.1 if subtotal >= 40 else 0
    return apply_discount(subtotal, rate)


def format_price(amount):
    return f"£{amount:.2f}"
