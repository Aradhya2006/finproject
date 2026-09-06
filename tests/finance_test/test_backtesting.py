import numpy as np
import pandas as pd

from src.risk.backtesting import (
    backtest_historical_var,
    calculate_violation_statistics,
)


dates = pd.date_range(
    start="2025-01-01",
    periods=10,
    freq="D",
)

returns = pd.Series(
    [
        0.01,
        -0.02,
        0.015,
        -0.01,
        0.005,
        -0.03,
        0.02,
        -0.015,
        0.01,
        -0.025,
    ],
    index=dates,
)


results = backtest_historical_var(
    returns,
    confidence_level=0.95,
    window=5,
)


print("Backtest Results")
print("-" * 50)
print(results)


statistics = calculate_violation_statistics(
    results,
    confidence_level=0.95,
)


print("\nViolation Statistics")
print("-" * 50)

for key, value in statistics.items():
    print(f"{key}: {value}")


assert len(results) == 5

assert "DATE" in results.columns
assert "ACTUAL RETURN" in results.columns
assert "VAR" in results.columns
assert "VIOLATION" in results.columns

assert statistics["total_observations"] == 5
assert statistics["violations"] == 1

assert np.isclose(
    statistics["violation_rate"],
    0.20,
)

assert np.isclose(
    statistics["expected_rate"],
    0.05,
)


print("\nHistorical VaR backtesting test passed!")