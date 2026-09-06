from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)


def test_multi_asset_dataset():

    symbols = [
        "TCS",
        "INFY",
        "HCLTECH",
        "WIPRO",
        "RELIANCE",
    ]

    prices = create_price_dataset(symbols)

    expected_columns = [
        "DATE",
        "TCS",
        "INFY",
        "HCLTECH",
        "WIPRO",
        "RELIANCE",
    ]

    assert list(prices.columns) == expected_columns
    assert prices["DATE"].is_monotonic_increasing
    assert not prices.duplicated("DATE").any()

    returns = calculate_asset_returns(prices)

    assert list(returns.columns) == expected_columns

    for symbol in symbols:
        assert returns[symbol].iloc[0] != returns[symbol].iloc[0]

    print("\nPrice dataset:")
    print(prices.head())

    print("\nReturn dataset:")
    print(returns.head())

    print(f"\nNumber of common trading days: {len(prices)}")


if __name__ == "__main__":
    test_multi_asset_dataset()
    print("\nMulti-asset dataset test passed!")