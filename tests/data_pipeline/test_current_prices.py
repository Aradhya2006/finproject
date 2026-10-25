from src.data.current_prices import (
    get_latest_prices,
)


def test_get_latest_prices():

    symbols = [
        "TCS",
        "INFY",
        "RELIANCE",
    ]

    raw = get_latest_prices(symbols)

    # get_latest_prices now includes a _sources metadata key
    sources = raw.pop("_sources", {})
    prices = raw

    print()
    print("CURRENT PRICE TEST")
    print("=" * 60)

    for symbol, price in prices.items():
        src = sources.get(symbol, "csv")
        print(
            f"{symbol}: ₹{price:.2f}  [source: {src}]"
        )

    assert set(prices.keys()) == set(symbols)

    for price in prices.values():
        assert isinstance(price, float)
        assert price > 0

    # Sources should map each symbol to 'live' or 'csv'
    for sym in symbols:
        assert sources.get(sym) in ("live", "csv"), (
            f"Unexpected source for {sym}: {sources.get(sym)}"
        )