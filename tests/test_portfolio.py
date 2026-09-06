import pandas as pd

from src.finance.portfolio import (
    calculate_holding_values,
    calculate_portfolio_value,
    calculate_portfolio_weights,
    calculate_portfolio_returns,
)


def test_portfolio():

    holdings = {
        "TCS": 10,
        "INFY": 20,
        "RELIANCE": 15,
    }

    prices = {
        "TCS": 4000,
        "INFY": 1500,
        "RELIANCE": 1400,
    }

    # Test holding values
    holding_values = calculate_holding_values(
        holdings,
        prices,
    )

    assert holding_values == {
        "TCS": 40000,
        "INFY": 30000,
        "RELIANCE": 21000,
    }

    # Test total portfolio value
    portfolio_value = calculate_portfolio_value(
        holding_values
    )

    assert portfolio_value == 91000

    # Test portfolio weights
    weights = calculate_portfolio_weights(
        holding_values
    )

    assert abs(sum(weights.values()) - 1) < 1e-10

    # Test portfolio returns
    asset_returns = pd.DataFrame({
        "TCS": [0.02, -0.015, 0.01],
        "INFY": [0.01, 0.005, -0.02],
        "RELIANCE": [-0.01, 0.02, 0.015],
    })

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    assert "PORTFOLIO RETURN" in portfolio_returns.columns

    # Check first portfolio return manually
    expected_first_return = (
        weights["TCS"] * 0.02
        + weights["INFY"] * 0.01
        + weights["RELIANCE"] * -0.01
    )

    assert abs(
        portfolio_returns["PORTFOLIO RETURN"].iloc[0]
        - expected_first_return
    ) < 1e-10

    print("Holding values:")
    print(holding_values)

    print(f"\nPortfolio value: ₹{portfolio_value:,.2f}")

    print("\nPortfolio weights:")
    for symbol, weight in weights.items():
        print(f"{symbol}: {weight * 100:.2f}%")

    print("\nPortfolio returns:")
    print(portfolio_returns)


if __name__ == "__main__":
    test_portfolio()
    print("\nPortfolio test passed!")