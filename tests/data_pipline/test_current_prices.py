from src.data.current_prices import (
    get_latest_prices,
)


def test_get_latest_prices():

    symbols = [
        "TCS",
        "INFY",
        "RELIANCE",
    ]

    prices = get_latest_prices(
        symbols
    )

    print()
    print("CURRENT PRICE TEST")
    print("=" * 60)

    for symbol, price in prices.items():
        print(
            f"{symbol}: ₹{price:.2f}"
        )

    assert set(prices.keys()) == set(
        symbols
    )

    for price in prices.values():
        assert isinstance(
            price,
            float,
        )

        assert price > 0