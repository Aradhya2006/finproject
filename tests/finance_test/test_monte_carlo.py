import numpy as np
import pandas as pd

from src.risk.monte_carlo import (
    simulate_portfolio_returns,
)


def test_monte_carlo():

    assets = [
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

    forecast_volatilities = pd.Series(
        {
            "TCS": 0.3097,
            "INFY": 0.2790,
            "HCLTECH": 0.2706,
            "WIPRO": 0.2247,
            "RELIANCE": 0.1795,
        }
    )

    correlation_matrix = pd.DataFrame(
        [
            [1.00, 0.39, 0.36, 0.33, 0.16],
            [0.39, 1.00, 0.40, 0.38, 0.15],
            [0.36, 0.40, 1.00, 0.36, 0.16],
            [0.33, 0.38, 0.36, 1.00, 0.13],
            [0.16, 0.15, 0.16, 0.13, 1.00],
        ],
        index=assets,
        columns=assets,
    )

    simulations = simulate_portfolio_returns(
        forecast_volatilities,
        correlation_matrix,
        weights,
        simulations=10000,
        horizon=21,
        seed=42,
    )

    print()
    print("MONTE CARLO SIMULATION")
    print("=" * 60)

    print(
        f"Shape: {simulations.shape}"
    )

    print(
        f"Mean daily return: "
        f"{simulations.mean():.6%}"
    )

    print(
        f"Daily volatility: "
        f"{simulations.std():.6%}"
    )

    assert simulations.shape == (
        10000,
        21,
    )

    assert np.all(
        np.isfinite(simulations)
    )