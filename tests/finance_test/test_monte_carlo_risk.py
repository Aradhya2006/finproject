import numpy as np

from src.risk.monte_carlo import (
    calculate_monte_carlo_var,
    calculate_monte_carlo_cvar,
)


def test_monte_carlo_risk():

    cumulative_returns = np.array(
        [
            -0.10,
            -0.08,
            -0.06,
            -0.04,
            -0.02,
            0.00,
            0.02,
            0.04,
            0.06,
            0.08,
            0.10,
        ]
    )

    var = calculate_monte_carlo_var(
        cumulative_returns,
        confidence_level=0.95,
    )

    cvar = calculate_monte_carlo_cvar(
        cumulative_returns,
        confidence_level=0.95,
    )

    print()
    print("MONTE CARLO RISK")
    print("=" * 60)

    print(
        f"95% VaR:  {var:.4%}"
    )

    print(
        f"95% CVaR: {cvar:.4%}"
    )

    assert var > 0
    assert cvar > 0

    assert cvar >= var