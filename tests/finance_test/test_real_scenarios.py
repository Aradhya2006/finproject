import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.risk.dynamic_asset_risk import (
    calculate_dynamic_asset_volatilities,
)
from src.finance.correlation import (
    calculate_correlation_matrix,
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


def test_real_portfolio_scenarios():

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

    # Load real NSE data.
    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    # Current EWMA asset volatility.
    asset_return_values = asset_returns.drop(
        columns=["DATE"]
    )

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

    simulations = 10000
    horizon = 21
    confidence_level = 0.95

    # Generate the same underlying Monte Carlo
    # asset paths for every scenario.
    asset_paths = simulate_asset_returns(
        forecast_volatilities=forecast_volatilities,
        correlation_matrix=correlation_matrix,
        simulations=simulations,
        horizon=horizon,
        seed=42,
    )

    assets = list(weights.keys())

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

    print()
    print("REAL PORTFOLIO SCENARIO SIMULATION")
    print("=" * 75)
    print(
        f"Simulations: {simulations:,}"
    )
    print(
        f"Horizon: {horizon} trading days"
    )
    print(
        f"Confidence level: {confidence_level:.0%}"
    )
    print()

    for scenario_name, shocks in scenarios.items():

        shocked_paths = (
            apply_shock_to_simulations(
                asset_paths,
                shocks,
                assets,
            )
        )

        portfolio_returns = (
            calculate_scenario_portfolio_returns(
                shocked_paths,
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
            confidence_level,
        )

        cvar = calculate_scenario_cvar(
            cumulative_returns,
            confidence_level,
        )

        mean_outcome = np.mean(
            cumulative_returns
        )

        median_outcome = np.median(
            cumulative_returns
        )

        worst_outcome = np.min(
            cumulative_returns
        )

        print(
            f"{scenario_name}"
        )
        print(
            f"  Mean outcome:   {mean_outcome:.4%}"
        )
        print(
            f"  Median outcome: {median_outcome:.4%}"
        )
        print(
            f"  Worst outcome:  {worst_outcome:.4%}"
        )
        print(
            f"  95% VaR:        {var:.4%}"
        )
        print(
            f"  95% CVaR:       {cvar:.4%}"
        )
        print()

    assert asset_paths.shape == (
        simulations,
        horizon,
        len(symbols),
    )