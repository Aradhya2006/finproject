from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import (
    calculate_portfolio_returns,
)

from src.risk.historical_var import (
    calculate_historical_var,
)

from src.risk.historical_cvar import (
    calculate_historical_cvar,
)


def test_historical_cvar():

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

    cvar_95 = calculate_historical_cvar(
        returns,
        confidence_level=0.95,
    )

    assert var_95 > 0
    assert cvar_95 > 0
    assert cvar_95 >= var_95

    print("\nHistorical CVaR")
    print("-" * 40)

    print(
        f"95% 1-day VaR: "
        f"{var_95 * 100:.2f}%"
    )

    print(
        f"95% 1-day CVaR: "
        f"{cvar_95 * 100:.2f}%"
    )


if __name__ == "__main__":
    test_historical_cvar()
    print("\nHistorical CVaR test passed!")