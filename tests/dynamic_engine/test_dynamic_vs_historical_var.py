import numpy as np
import pandas as pd

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)



from src.risk.backtesting import (
    backtest_historical_var,
)

from src.risk.dynamic_backtesting import (
    backtest_dynamic_ewma_var,
)

from src.risk.kupiec import (
    calculate_kupiec_test,
)

from src.risk.christoffersen import (
    calculate_christoffersen_test,
    calculate_conditional_coverage_test,
)


def summarize_backtest(results):

    violations = int(
        results["VIOLATION"].sum()
    )

    violation_rate = (
        violations / len(results)
    )

    violation_returns = results.loc[
        results["VIOLATION"],
        "ACTUAL RETURN",
    ]

    average_violation = (
        violation_returns.mean()
        if len(violation_returns) > 0
        else np.nan
    )

    worst_return = results[
        "ACTUAL RETURN"
    ].min()

    if "VAR" in results.columns:
        var_column = "VAR"
    elif "VAR RETURN" in results.columns:
        var_column = "VAR RETURN"
    else:
        raise ValueError(
            "Backtest results must contain "
            "'VAR' or 'VAR RETURN'."
        )

    return {
        "observations": len(results),
        "violations": violations,
        "violation_rate": violation_rate,
        "average_violation": average_violation,
        "worst_return": worst_return,
        "average_var": results[var_column].mean(),
    }
    
    

def test_dynamic_vs_historical_var():

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

    # Portfolio returns
    portfolio_returns = (
        asset_returns
        .set_index("DATE")
        .loc[:, symbols]
        .mul(
            [weights[s] for s in symbols],
            axis=1,
        )
        .sum(axis=1)
    )

    # --------------------------------------------------
    # Historical VaR
    # --------------------------------------------------

    historical_results = (
        backtest_historical_var(
            portfolio_returns,
            confidence_level=0.95,
            window=252,
        )
    )

    # --------------------------------------------------
    # Dynamic EWMA VaR
    # --------------------------------------------------

    asset_returns_indexed = (
        asset_returns
        .set_index("DATE")
        [symbols]
    )

    

    dynamic_results = (
        backtest_dynamic_ewma_var(
            asset_returns_indexed,
            weights,
            confidence_level=0.95,
            lambda_=0.94,
            window=252,
        )
    )
    # --------------------------------------------------
# Align both models to identical test dates
# --------------------------------------------------

    historical_results = historical_results.copy()
    dynamic_results = dynamic_results.copy()

    historical_results["DATE"] = pd.to_datetime(
        historical_results["DATE"]
    )

    dynamic_results["DATE"] = pd.to_datetime(
        dynamic_results["DATE"]
    )

    common_dates = np.intersect1d(
        historical_results["DATE"].values,
        dynamic_results["DATE"].values,
    )

    historical_results = (
        historical_results[
            historical_results["DATE"].isin(common_dates)
        ]
        .sort_values("DATE")
        .reset_index(drop=True)
    )

    dynamic_results = (
        dynamic_results[
            dynamic_results["DATE"].isin(common_dates)
        ]
        .sort_values("DATE")
        .reset_index(drop=True)
    )

    assert len(historical_results) == len(
        dynamic_results
    )

    assert np.array_equal(
        historical_results["DATE"].values,
        dynamic_results["DATE"].values,
    )

    # --------------------------------------------------
    # Validation tests
    # --------------------------------------------------

    historical_kupiec = (
        calculate_kupiec_test(
            historical_results,
            confidence_level=0.95,
        )
    )

    historical_christoffersen = (
        calculate_christoffersen_test(
            historical_results
        )
    )

    historical_conditional = (
        calculate_conditional_coverage_test(
            historical_kupiec,
            historical_christoffersen,
        )
    )

    dynamic_kupiec = (
        calculate_kupiec_test(
            dynamic_results,
            confidence_level=0.95,
        )
    )

    dynamic_christoffersen = (
        calculate_christoffersen_test(
            dynamic_results
        )
    )

    dynamic_conditional = (
        calculate_conditional_coverage_test(
            dynamic_kupiec,
            dynamic_christoffersen,
        )
    )

    historical_summary = summarize_backtest(
        historical_results
    )

    dynamic_summary = summarize_backtest(
        dynamic_results
    )

    # --------------------------------------------------
    # Display
    # --------------------------------------------------

    print()
    print("DYNAMIC VS HISTORICAL VAR")
    print("=" * 70)

    print()
    print("BACKTEST PERFORMANCE")
    print("-" * 70)

    print(
        f"{'Metric':<30}"
        f"{'Historical':>18}"
        f"{'Dynamic EWMA':>18}"
    )

    print(
        f"{'Observations':<30}"
        f"{historical_summary['observations']:>18}"
        f"{dynamic_summary['observations']:>18}"
    )

    print(
        f"{'Violations':<30}"
        f"{historical_summary['violations']:>18}"
        f"{dynamic_summary['violations']:>18}"
    )

    print(
        f"{'Violation rate':<30}"
        f"{historical_summary['violation_rate']:>17.4%}"
        f"{dynamic_summary['violation_rate']:>17.4%}"
    )

    print(
        f"{'Average VaR':<30}"
        f"{historical_summary['average_var']:>17.4%}"
        f"{dynamic_summary['average_var']:>17.4%}"
    )

    print(
        f"{'Average violation':<30}"
        f"{historical_summary['average_violation']:>17.4%}"
        f"{dynamic_summary['average_violation']:>17.4%}"
    )

    print(
        f"{'Worst actual return':<30}"
        f"{historical_summary['worst_return']:>17.4%}"
        f"{dynamic_summary['worst_return']:>17.4%}"
    )

    print()
    print("KUPIEC TEST")
    print("-" * 70)

    print(
        f"Historical p-value: "
        f"{historical_kupiec['p_value']:.6f}"
    )

    print(
        f"Dynamic p-value:    "
        f"{dynamic_kupiec['p_value']:.6f}"
    )

    print()
    print("CHRISTOFFERSEN TEST")
    print("-" * 70)

    print(
        f"Historical p-value: "
        f"{historical_christoffersen['p_value']:.6f}"
    )

    print(
        f"Dynamic p-value:    "
        f"{dynamic_christoffersen['p_value']:.6f}"
    )

    print()
    print("CONDITIONAL COVERAGE")
    print("-" * 70)

    print(
        f"Historical p-value: "
        f"{historical_conditional['p_value']:.6f}"
    )

    print(
        f"Dynamic p-value:    "
        f"{dynamic_conditional['p_value']:.6f}"
    )

    print()

    assert len(historical_results) > 0
    assert len(dynamic_results) > 0

    assert np.isfinite(
        historical_kupiec["p_value"]
    )

    assert np.isfinite(
        dynamic_kupiec["p_value"]
    )