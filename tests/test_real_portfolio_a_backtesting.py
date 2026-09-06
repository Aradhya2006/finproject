import numpy as np
import pandas as pd
from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.risk.kupiec import calculate_kupiec_test
from src.finance.portfolio import (
    calculate_portfolio_returns,
)

from src.risk.backtesting import (
    backtest_historical_var,
    calculate_violation_statistics,
)


# --------------------------------------------------
# Portfolio A
# --------------------------------------------------

PORTFOLIO_A_WEIGHTS = {
    "TCS": 0.25,
    "INFY": 0.25,
    "HCLTECH": 0.20,
    "WIPRO": 0.15,
    "RELIANCE": 0.15,
}


# --------------------------------------------------
# Load real NSE price data
# --------------------------------------------------

symbols = list(PORTFOLIO_A_WEIGHTS.keys())

price_data = create_price_dataset(symbols)

print("Price Dataset")
print("-" * 60)
print(f"Start date: {price_data['DATE'].min()}")
print(f"End date:   {price_data['DATE'].max()}")
print(f"Rows:       {len(price_data)}")


# --------------------------------------------------
# Calculate asset returns
# --------------------------------------------------

asset_returns = calculate_asset_returns(
    price_data
)


# --------------------------------------------------
# Calculate portfolio returns
# --------------------------------------------------

portfolio_data = calculate_portfolio_returns(
    asset_returns,
    PORTFOLIO_A_WEIGHTS,
)

portfolio_returns = pd.Series(
    portfolio_data["PORTFOLIO RETURN"].values,
    index=portfolio_data["DATE"],
)


print("\nPortfolio A")
print("-" * 60)

print("Weights:")

for symbol, weight in PORTFOLIO_A_WEIGHTS.items():
    print(f"{symbol}: {weight:.2%}")


print(
    f"\nPortfolio return observations: "
    f"{portfolio_returns.dropna().shape[0]}"
)


# --------------------------------------------------
# Historical VaR Backtest
# --------------------------------------------------

backtest_results = backtest_historical_var(
    portfolio_returns,
    confidence_level=0.95,
    window=252,
)


print("\nBacktest Results")
print("-" * 60)

print(
    backtest_results.head()
)

print("\n...")
print(
    backtest_results.tail()
)


# --------------------------------------------------
# Violation statistics
# --------------------------------------------------

statistics = calculate_violation_statistics(
    backtest_results,
    confidence_level=0.95,
)

violations = backtest_results[
    backtest_results["VIOLATION"]
]

print("\nViolation Dates")
print("-" * 60)

print(
    violations[
        [
            "DATE",
            "ACTUAL RETURN",
            "VAR",
        ]
    ].to_string(index=False)
)


print("\nViolation Analysis")
print("-" * 60)

print(
    f"Number of violations: "
    f"{len(violations)}"
)

print(
    f"Worst actual return: "
    f"{violations['ACTUAL RETURN'].min():.2%}"
)

print(
    f"Average return on violation days: "
    f"{violations['ACTUAL RETURN'].mean():.2%}"
)
print("\nViolation Statistics")
print("-" * 60)

print(
    f"Total observations: "
    f"{statistics['total_observations']}"
)

print(
    f"Violations: "
    f"{statistics['violations']}"
)

print(
    f"Violation rate: "
    f"{statistics['violation_rate']:.2%}"
)

print(
    f"Expected rate: "
    f"{statistics['expected_rate']:.2%}"
)


# --------------------------------------------------
# Basic validation
# --------------------------------------------------

assert len(price_data) > 0

assert not portfolio_returns.dropna().empty

assert len(backtest_results) > 0

assert (
    statistics["total_observations"]
    == len(backtest_results)
)

assert (
    0 <= statistics["violation_rate"] <= 1
)

assert np.isclose(
    statistics["expected_rate"],
    0.05,
)


print(
    "\nReal Portfolio A VaR backtesting test passed!"
)# --------------------------------------------------
# Kupiec Unconditional Coverage Test
# --------------------------------------------------

kupiec_results = calculate_kupiec_test(
    backtest_results,
    confidence_level=0.95,
)


print("\nKupiec Unconditional Coverage Test")
print("-" * 60)

print(
    f"Total observations: "
    f"{kupiec_results['total_observations']}"
)

print(
    f"Violations: "
    f"{kupiec_results['violations']}"
)

print(
    f"Expected probability: "
    f"{kupiec_results['expected_probability']:.2%}"
)

print(
    f"Observed probability: "
    f"{kupiec_results['observed_probability']:.2%}"
)

print(
    f"Likelihood ratio: "
    f"{kupiec_results['likelihood_ratio']:.6f}"
)

print(
    f"P-value: "
    f"{kupiec_results['p_value']:.6f}"
)

# --------------------------------------------------
# Basic validation
# --------------------------------------------------

assert kupiec_results["total_observations"] == 2642

assert kupiec_results["violations"] == 142

assert np.isclose(
    kupiec_results["expected_probability"],
    0.05,
)

assert np.isclose(
    kupiec_results["observed_probability"],
    142 / 2642,
)

assert kupiec_results["likelihood_ratio"] >= 0

assert 0 <= kupiec_results["p_value"] <= 1