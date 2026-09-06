from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.correlation import (
    calculate_covariance_matrix,
    calculate_correlation_matrix,
)


def test_correlation():

    symbols = [
        "TCS",
        "INFY",
        "HCLTECH",
        "WIPRO",
        "RELIANCE",
    ]

    prices = create_price_dataset(symbols)
    returns = calculate_asset_returns(prices)

    covariance_matrix = calculate_covariance_matrix(
        returns
    )

    correlation_matrix = calculate_correlation_matrix(
        returns
    )

    assert covariance_matrix.shape == (5, 5)
    assert correlation_matrix.shape == (5, 5)

    assert list(covariance_matrix.columns) == symbols
    assert list(correlation_matrix.columns) == symbols

    assert (correlation_matrix.values.diagonal() == 1).all()

    print("\nCovariance matrix:")
    print(covariance_matrix)

    print("\nCorrelation matrix:")
    print(correlation_matrix)


if __name__ == "__main__":
    test_correlation()
    print("\nCorrelation test passed!")