from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.correlation import (
    calculate_covariance_matrix,
)

from src.finance.portfolio import (
    calculate_holding_values,
    calculate_portfolio_value,
    calculate_portfolio_weights,
)

from src.finance.portfolio_risk import (
    calculate_portfolio_variance,
    calculate_portfolio_volatility,
)


def test_portfolio_risk():

    symbols = [
        "TCS",
        "INFY",
        "HCLTECH",
        "WIPRO",
        "RELIANCE",
    ]

    # Load real historical prices
    prices = create_price_dataset(symbols)

    # Calculate historical returns
    returns = calculate_asset_returns(prices)

    # Calculate covariance matrix
    covariance_matrix = calculate_covariance_matrix(
        returns
    )

    # Portfolio A
    weights = {
    "TCS": 0.25,
    "INFY": 0.25,
    "HCLTECH": 0.20,
    "WIPRO": 0.15,
    "RELIANCE": 0.15,
}



    portfolio_variance = calculate_portfolio_variance(
        weights,
        covariance_matrix,
    )

    portfolio_volatility = calculate_portfolio_volatility(
        weights,
        covariance_matrix,
    )

    assert portfolio_variance > 0
    assert portfolio_volatility > 0

    print("\nPortfolio A")
    print("-" * 40)

    # print(f"Portfolio value: ₹{portfolio_value:,.2f}")

    print("\nWeights:")
    for symbol, weight in weights.items():
        print(
            f"{symbol}: {weight * 100:.2f}%"
        )

    print(
        f"\nPortfolio variance: "
        f"{portfolio_variance:.8f}"
    )

    print(
        f"Daily portfolio volatility: "
        f"{portfolio_volatility:.6f}"
    )

    print(
        f"Annualized portfolio volatility: "
        f"{portfolio_volatility * 100 * (252 ** 0.5):.2f}%"
    )


if __name__ == "__main__":
    test_portfolio_risk()
    print("\nPortfolio risk test passed!")