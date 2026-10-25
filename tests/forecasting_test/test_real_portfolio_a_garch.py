import numpy as np

from src.finance.dataset import create_price_dataset, calculate_asset_returns
from src.finance.portfolio import calculate_portfolio_returns
from src.forecasting.garch import (
    fit_garch,
    calculate_garch_volatility,
    calculate_annualized_garch_volatility,
    forecast_garch_volatility,
)


def test_real_portfolio_a_garch():

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

    price_data = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(price_data)

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    returns = portfolio_returns["PORTFOLIO RETURN"]

    result = fit_garch(returns)

    daily_volatility = calculate_garch_volatility(result)

    annualized_volatility = calculate_annualized_garch_volatility(result)

    forecast = forecast_garch_volatility(
        result,
        horizon=5,
    )

    print("\n" + "=" * 60)
    print("PORTFOLIO A — GARCH(1,1)")
    print("=" * 60)

    print("\nGARCH PARAMETERS")
    print(result.params)

    alpha = result.params["alpha[1]"]
    beta = result.params["beta[1]"]

    print("\nVOLATILITY PERSISTENCE")
    print(f"alpha + beta: {alpha + beta:.6f}")

    print("\nVOLATILITY")
    print(
        f"Latest daily volatility: "
        f"{daily_volatility.iloc[-1]:.6f}"
    )

    print(
        f"Latest annualized volatility: "
        f"{annualized_volatility.iloc[-1]:.2%}"
    )

    print("\n5-DAY VOLATILITY FORECAST")

    for day, volatility in forecast.items():
        print(
            f"Day {day}: {volatility:.6f} "
            f"({volatility * np.sqrt(252):.2%} annualized)"
        )

    print("=" * 60)

    assert np.isfinite(alpha)
    assert np.isfinite(beta)

    assert alpha >= 0
    assert beta >= 0

    assert np.isfinite(daily_volatility).all()
    assert np.isfinite(annualized_volatility).all()

    assert (daily_volatility > 0).all()
    assert (annualized_volatility > 0).all()

    assert len(forecast) == 5
    assert np.isfinite(forecast).all()
    assert (forecast > 0).all()