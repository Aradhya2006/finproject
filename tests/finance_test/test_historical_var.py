from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import (
    calculate_portfolio_returns,
)

from src.risk.historical_var import (
    calculate_historical_var,
    calculate_var_value,
)


def test_historical_var():

    symbols = [
        "TCS",
        "INFY",
        "HCLTECH",
        "WIPRO",
        "RELIANCE",
    ]

    weights = {
        "TCS": 0.25,
        "INFY": 0.25,
        "HCLTECH": 0.20,
        "WIPRO": 0.15,
        "RELIANCE": 0.15,
    }

    prices = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(
        prices
    )

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    returns = portfolio_returns[
        "PORTFOLIO RETURN"
    ]

    var_95 = calculate_historical_var(
        returns,
        confidence_level=0.95,
    )

    portfolio_value = 1_000_000

    var_value = calculate_var_value(var_95,portfolio_value)   
    assert var_95 > 0
    assert var_value > 0

    print("\nHistorical VaR")
    print("-" * 40)

    print(
    f"Portfolio value: "
    f"₹{portfolio_value:,.2f}")

    print(
    f"95% 1-day VaR: "
    f"{var_95 * 100:.2f}%")

    print(
    f"95% 1-day VaR amount: "
    f"₹{var_value:,.2f}")


if __name__ == "__main__":
    test_historical_var()
    print("\nHistorical VaR test passed!")