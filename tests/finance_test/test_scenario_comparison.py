import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.correlation import (
    calculate_correlation_matrix,
)
from src.risk.dynamic_asset_risk import (
    calculate_dynamic_asset_volatilities,
)
from src.risk.monte_carlo import (
    simulate_asset_returns,
)
from src.risk.scenario import (
    apply_shock_to_simulations,
    calculate_scenario_portfolio_returns,
    calculate_scenario_cumulative_returns,
    calculate_scenario_var,
    calculate_scenario_cvar,
)


def test_scenario_comparison():

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

    # ---------------------------------------------------------
    # 1. Load real NSE data
    # ---------------------------------------------------------

    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    asset_return_values = (
        asset_returns.drop(
            columns=["DATE"]
        )
    )

    # ---------------------------------------------------------
    # 2. Current volatility and correlation
    # ---------------------------------------------------------

    forecast_volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_return_values
        )
    )

    correlation_matrix = (
        calculate_correlation_matrix(
            asset_returns
        )
    )

    # ---------------------------------------------------------
    # 3. Generate common Monte Carlo paths
    # ---------------------------------------------------------

    simulations = 10000
    horizon = 21
    confidence_level = 0.95

    asset_paths = simulate_asset_returns(
        forecast_volatilities=forecast_volatilities,
        correlation_matrix=correlation_matrix,
        simulations=simulations,
        horizon=horizon,
        seed=42,
    )

    assets = list(weights.keys())

    # ---------------------------------------------------------
    # 4. Baseline: normal market
    # ---------------------------------------------------------

    baseline_portfolio_returns = (
        calculate_scenario_portfolio_returns(
            asset_paths,
            weights,
        )
    )

    baseline_outcomes = (
        calculate_scenario_cumulative_returns(
            baseline_portfolio_returns
        )
    )

    baseline_var = calculate_scenario_var(
        baseline_outcomes,
        confidence_level,
    )

    baseline_cvar = calculate_scenario_cvar(
        baseline_outcomes,
        confidence_level,
    )

    # ---------------------------------------------------------
    # 5. Define scenarios
    # ---------------------------------------------------------

    scenarios = {
        "IT Sector Crash": {
            "TCS": -0.20,
            "INFY": -0.20,
            "HCLTECH": -0.20,
            "WIPRO": -0.20,
            "RELIANCE": -0.10,
        },
        "Broad Market Crash": {
            "TCS": -0.15,
            "INFY": -0.15,
            "HCLTECH": -0.15,
            "WIPRO": -0.15,
            "RELIANCE": -0.15,
        },
        "Reliance Shock": {
            "TCS": -0.05,
            "INFY": -0.05,
            "HCLTECH": -0.05,
            "WIPRO": -0.05,
            "RELIANCE": -0.30,
        },
        "Moderate Downturn": {
            "TCS": -0.10,
            "INFY": -0.10,
            "HCLTECH": -0.10,
            "WIPRO": -0.10,
            "RELIANCE": -0.10,
        },
    }

    # ---------------------------------------------------------
    # 6. Print comparison
    # ---------------------------------------------------------

    print()
    print("MONTE CARLO SCENARIO COMPARISON")
    print("=" * 90)

    print(
        f"{'Scenario':<25}"
        f"{'Mean Outcome':>15}"
        f"{'95% VaR':>15}"
        f"{'95% CVaR':>15}"
        f"{'VaR Increase':>15}"
    )

    print("-" * 90)

    print(
        f"{'Normal Market':<25}"
        f"{np.mean(baseline_outcomes):>14.2%}"
        f"{baseline_var:>14.2%}"
        f"{baseline_cvar:>14.2%}"
        f"{'Baseline':>15}"
    )

    for scenario_name, shocks in scenarios.items():

        shocked_paths = (
            apply_shock_to_simulations(
                asset_paths,
                shocks,
                assets,
            )
        )

        scenario_portfolio_returns = (
            calculate_scenario_portfolio_returns(
                shocked_paths,
                weights,
            )
        )

        scenario_outcomes = (
            calculate_scenario_cumulative_returns(
                scenario_portfolio_returns
            )
        )

        scenario_var = calculate_scenario_var(
            scenario_outcomes,
            confidence_level,
        )

        scenario_cvar = calculate_scenario_cvar(
            scenario_outcomes,
            confidence_level,
        )

        var_increase = (
            scenario_var - baseline_var
        )

        print(
            f"{scenario_name:<25}"
            f"{np.mean(scenario_outcomes):>14.2%}"
            f"{scenario_var:>14.2%}"
            f"{scenario_cvar:>14.2%}"
            f"{var_increase:>14.2%}"
        )

    print("-" * 90)

    print()
    print(
        f"Baseline 95% VaR:  "
        f"{baseline_var:.4%}"
    )

    print(
        f"Baseline 95% CVaR: "
        f"{baseline_cvar:.4%}"
    )

    assert baseline_var >= 0
    assert baseline_cvar >= baseline_var

    assert asset_paths.shape == (
        simulations,
        horizon,
        len(symbols),
    )