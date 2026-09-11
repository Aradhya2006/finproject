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
)


def test_real_monte_carlo():

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

    # --------------------------------------------------
    # Load actual Portfolio A data
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Current dynamic asset volatility
    # --------------------------------------------------

    forecast_volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_returns,
            lambda_=0.94,
        )
    )

    # --------------------------------------------------
    # Current correlation
    #
    # This is for the current simulation only.
    # It is NOT being used for backtesting.
    # --------------------------------------------------

    correlation_matrix = (
        asset_returns.corr()
    )

    # --------------------------------------------------
    # Monte Carlo simulation
    # --------------------------------------------------

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

    cumulative_returns = (
        calculate_cumulative_returns(
            simulated_returns
        )
    )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    print()
    print("REAL PORTFOLIO A MONTE CARLO")
    print("=" * 60)

    print(
        f"Simulations: "
        f"{len(cumulative_returns):,}"
    )

    print(
        f"Horizon: "
        f"{simulated_returns.shape[1]} trading days"
    )

    print(
        f"Mean outcome: "
        f"{cumulative_returns.mean():.4%}"
    )

    print(
        f"Median outcome: "
        f"{np.median(cumulative_returns):.4%}"
    )

    print(
        f"Worst simulated outcome: "
        f"{cumulative_returns.min():.4%}"
    )

    print(
        f"Best simulated outcome: "
        f"{cumulative_returns.max():.4%}"
    )

    print(
        f"5th percentile: "
        f"{np.percentile(cumulative_returns, 5):.4%}"
    )

    print(
        f"95th percentile: "
        f"{np.percentile(cumulative_returns, 95):.4%}"
    )

    print()

    assert simulated_returns.shape == (
        10000,
        21,
    )

    assert cumulative_returns.shape == (
        10000,
    )

    assert np.all(
        np.isfinite(cumulative_returns)
    )