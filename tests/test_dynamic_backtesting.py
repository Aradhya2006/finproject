import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.correlation import (
    calculate_correlation_matrix,
)

from src.risk.dynamic_backtesting import (
    backtest_dynamic_ewma_var,
)


def test_dynamic_backtesting():

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

    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    asset_returns = asset_returns.set_index(
        "DATE"
    )

    correlation_matrix = (
        calculate_correlation_matrix(
            asset_returns.reset_index()
        )
    )

    results = backtest_dynamic_ewma_var(
        asset_returns,
        weights,
        correlation_matrix,
        confidence_level=0.95,
        lambda_=0.94,
        window=252,
    )

    violations = (
        results["VIOLATION"].sum()
    )

    violation_rate = (
        violations / len(results)
    )

    print()
    print("DYNAMIC EWMA VAR BACKTEST")
    print("=" * 60)

    print(
        f"Observations: {len(results)}"
    )

    print(
        f"Violations: {violations}"
    )

    print(
        f"Violation rate: "
        f"{violation_rate:.4%}"
    )

    print(
        f"Expected rate: "
        f"{1 - 0.95:.4%}"
    )

    print(
        f"Average forecast volatility: "
        f"{results['FORECAST VOLATILITY'].mean():.4%}"
    )

    assert len(results) > 0

    assert np.all(
        np.isfinite(
            results["ACTUAL RETURN"]
        )
    )

    assert np.all(
        np.isfinite(
            results["VAR RETURN"]
        )
    )

    assert np.all(
        results["FORECAST VOLATILITY"] > 0
    )