from calc import basket_total, format_price


def main():
    basket = [(12.50, 2), (5.00, 4)]
    total = basket_total(basket)
    print(f"Total: {format_price(total)}")


if __name__ == "__main__":
    main()
