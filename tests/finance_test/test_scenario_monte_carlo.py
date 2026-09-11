import numpy as np

from src.risk.scenario import (
    apply_shock_to_simulations,
    calculate_scenario_portfolio_returns,
    calculate_scenario_cumulative_returns,
    calculate_scenario_var,
    calculate_scenario_cvar,
)


def test_scenario_monte_carlo():

    assets = [
        "TCS",
        "RELIANCE",
    ]

    weights = {
        "TCS": 0.60,
        "RELIANCE": 0.40,
    }

    simulated_returns = np.array([
        [
            [0.01, 0.02],
            [0.01, 0.01],
            [0.02, -0.01],
        ],
        [
            [0.02, 0.01],
            [-0.01, 0.02],
            [0.01, 0.01],
        ],
        [
            [0.00, 0.01],
            [0.01, -0.02],
            [-0.01, 0.02],
        ],
    ])

    shocks = {
        "TCS": -0.20,
        "RELIANCE": -0.10,
    }

    shocked_returns = apply_shock_to_simulations(
        simulated_returns,
        shocks,
        assets,
    )

    # Day 1 must contain the exact scenario shock.
    assert np.all(
        shocked_returns[:, 0, 0] == -0.20
    )

    assert np.all(
        shocked_returns[:, 0, 1] == -0.10
    )

    # Later days must remain unchanged.
    assert np.array_equal(
        shocked_returns[:, 1:, :],
        simulated_returns[:, 1:, :],
    )

    portfolio_returns = (
        calculate_scenario_portfolio_returns(
            shocked_returns,
            weights,
        )
    )

    cumulative_returns = (
        calculate_scenario_cumulative_returns(
            portfolio_returns
        )
    )

    var = calculate_scenario_var(
        cumulative_returns,
        confidence_level=0.95,
    )

    cvar = calculate_scenario_cvar(
        cumulative_returns,
        confidence_level=0.95,
    )

    print()
    print("SCENARIO MONTE CARLO TEST")
    print("=" * 60)
    print(
        "Simulation shape:",
        shocked_returns.shape,
    )
    print(
        "Cumulative outcomes:",
        cumulative_returns,
    )
    print(
        f"95% Scenario VaR: {var:.4%}"
    )
    print(
        f"95% Scenario CVaR: {cvar:.4%}"
    )

    assert shocked_returns.shape == (
        3,
        3,
        2,
    )

    assert var >= 0
    assert cvar >= var