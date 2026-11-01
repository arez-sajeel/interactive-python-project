# Scenario A: prompt record

## Attempt 1

- **Model:** GPT-6 (ChatGPT)
- **Date:** 2026-11-01
- **Chat:** new chat

### Prompt

> Write a small Python project with two files. `calc.py` should have functions to work out
> the total of a shopping basket, given a list of (price, quantity) pairs, and apply a 10%
> discount when the subtotal is £40 or more. It should also format a price as pounds and
> pence. `main.py` should build a sample basket, call `calc.py` and print the total. Keep it
> short and do not add tests.

### Output

The reply below is unedited, except that line breaks and indentation in the code were
restored after copying from ChatGPT.

Here is a small Python project with two files. It uses `Decimal` for accurate currency calculations.

### Project structure

```
shopping_basket/
├── calc.py
└── main.py
```

### 1. calc.py

```python
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
```

### 2. main.py

```python
from calc import basket_total, format_price

# Sample shopping basket: (price, quantity)
basket = [
    (12.50, 2),
    (8.00, 1),
    (5.50, 2)
]

total = basket_total(basket)
print("Shopping Basket Total:", format_price(total))
```

### Example output

```
Shopping Basket Total: £39.60
```

How it works:

- `basket_total()` multiplies each item's price by its quantity.
- A 10% discount is applied when the subtotal is £40 or more.
- `format_price()` displays the result with a £ symbol and two decimal places.
- `main.py` creates a sample basket and prints the calculated total.

## Attempt 2

- **Model:** GPT-6 (ChatGPT)
- **Date:** 2026-11-01
- **Chat:** new chat

### Prompt

Same prompt as attempt 1.

### Output

The reply below is unedited, except that line breaks and indentation in the code were
restored after copying from ChatGPT.

Create the following two files in the same directory.

### 1. `calc.py`

Contains the basket calculation, discount logic and price formatting.

```python
def calculate_total(basket):
    subtotal = sum(price * quantity for price, quantity in basket)

    if subtotal >= 40:
        subtotal *= 0.90  # Apply 10% discount

    return subtotal


def format_price(amount):
    return f"£{amount:.2f}"
```

### 2. `main.py`

Builds a sample basket, imports the functions from `calc.py` and prints the total.

```python
from calc import calculate_total, format_price

basket = [
    (12.50, 2),
    (5.00, 1),
    (8.00, 1)
]

total = calculate_total(basket)
print("Basket total:", format_price(total))
```

### Run the project

Open a terminal in the project directory and run:

```
python main.py
```

Expected output:

```
Basket total: £34.20
```

The subtotal is £38.00, so no discount is applied.
