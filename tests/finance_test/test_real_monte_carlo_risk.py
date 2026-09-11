import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.risk.dynamic_asset_risk import (
    calculate_dynamic_asset_volatilities,
)

from src.risk.monte_carlo import (
    simulate_portfolio_returns,
    calculate_cumulative_returns,
    calculate_monte_carlo_var,
    calculate_monte_carlo_cvar,
)


def test_real_monte_carlo_risk():

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

    # Load actual data
    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    asset_returns = (
        asset_returns
        .set_index("DATE")
        [symbols]
    )

    # Current EWMA asset volatility
    forecast_volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_returns,
            lambda_=0.94,
        )
    )

    # Current correlation
    correlation_matrix = (
        asset_returns.corr()
    )

    # Simulate 21 trading days
    simulated_returns = (
        simulate_portfolio_returns(
            forecast_volatilities,
            correlation_matrix,
            weights,
            simulations=10000,
            horizon=21,
            seed=42,
        )
    )

    # Convert paths to cumulative outcomes
    cumulative_returns = (
        calculate_cumulative_returns(
            simulated_returns
        )
    )

    # Calculate Monte Carlo risk
    var = calculate_monte_carlo_var(
        cumulative_returns,
        confidence_level=0.95,
    )

    cvar = calculate_monte_carlo_cvar(
        cumulative_returns,
        confidence_level=0.95,
    )

    print()
    print("REAL PORTFOLIO A MONTE CARLO RISK")
    print("=" * 60)

    print(
        f"Simulations: 10,000"
    )

    print(
        f"Horizon: 21 trading days"
    )

    print(
        f"95% VaR:  {var:.4%}"
    )

    print(
        f"95% CVaR: {cvar:.4%}"
    )

    print(
        f"VaR amount on ₹10 lakh: "
        f"₹{var * 1_000_000:,.2f}"
    )

    print(
        f"CVaR amount on ₹10 lakh: "
        f"₹{cvar * 1_000_000:,.2f}"
    )

    print()

    assert var > 0
    assert cvar > 0

    assert cvar >= var

    assert np.isfinite(var)
    assert np.isfinite(cvar)