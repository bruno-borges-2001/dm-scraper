def format_price(price: str) -> float:
    """Converts a string price to a float."""
    return float(
        price
        .removeprefix("R$")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )
