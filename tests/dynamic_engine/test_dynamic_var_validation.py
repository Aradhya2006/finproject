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

from src.risk.kupiec import (
    calculate_kupiec_test,
)

from src.risk.christoffersen import (
    calculate_christoffersen_test,
    calculate_conditional_coverage_test,
)


def test_dynamic_var_validation():

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

    backtest_results = backtest_dynamic_ewma_var(
        asset_returns,
        weights,
        correlation_matrix,
        confidence_level=0.95,
        lambda_=0.94,
        window=252,
    )

    kupiec_results = calculate_kupiec_test(
        backtest_results,
        confidence_level=0.95,
    )

    christoffersen_results = (
        calculate_christoffersen_test(
            backtest_results
        )
    )

    conditional_results = (
        calculate_conditional_coverage_test(
            kupiec_results,
            christoffersen_results,
        )
    )

    print()
    print("DYNAMIC VAR VALIDATION")
    print("=" * 60)

    print()
    print("KUPIEC TEST")
    print(
        f"Violations: "
        f"{kupiec_results['violations']}"
    )
    print(
        f"Observed probability: "
        f"{kupiec_results['observed_probability']:.4%}"
    )
    print(
        f"Likelihood ratio: "
        f"{kupiec_results['likelihood_ratio']:.6f}"
    )
    print(
        f"p-value: "
        f"{kupiec_results['p_value']:.6f}"
    )

    print()
    print("CHRISTOFFERSEN TEST")
    print(
        f"N00: {christoffersen_results['n00']}"
    )
    print(
        f"N01: {christoffersen_results['n01']}"
    )
    print(
        f"N10: {christoffersen_results['n10']}"
    )
    print(
        f"N11: {christoffersen_results['n11']}"
    )
    print(
        f"P(V|no V): "
        f"{christoffersen_results['pi01']:.4%}"
    )
    print(
        f"P(V|V): "
        f"{christoffersen_results['pi11']:.4%}"
    )
    print(
        f"Likelihood ratio: "
        f"{christoffersen_results['likelihood_ratio']:.6f}"
    )
    print(
        f"p-value: "
        f"{christoffersen_results['p_value']:.6f}"
    )

    print()
    print("CONDITIONAL COVERAGE TEST")
    print(
        f"Likelihood ratio: "
        f"{conditional_results['likelihood_ratio']:.6f}"
    )
    print(
        f"p-value: "
        f"{conditional_results['p_value']:.6f}"
    )

    print()

    assert np.isfinite(
        kupiec_results["p_value"]
    )

    assert np.isfinite(
        christoffersen_results["p_value"]
    )

    assert np.isfinite(
        conditional_results["p_value"]
    )