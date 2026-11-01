from calc import basket_total, format_price

# Sample shopping basket: (price, quantity)
basket = [
    (12.50, 2),
    (8.00, 1),
    (5.50, 2)
]

total = basket_total(basket)
print("Shopping Basket Total:", format_price(total))
