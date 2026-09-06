import numpy as np
import pandas as pd


def backtest_historical_var(
    portfolio_returns,
    confidence_level=0.95,
    window=252,
):
    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if window <= 0:
        raise ValueError(
            "window must be greater than zero."
        )

    returns = portfolio_returns.dropna()

    if len(returns) <= window:
        raise ValueError(
            "Not enough returns for the selected window."
        )

    results = []

    tail_probability = 1 - confidence_level

    for i in range(window, len(returns)):
        historical_window = returns.iloc[i - window:i]

        var_threshold = np.percentile(
            historical_window,
            tail_probability * 100,
        )

        var = -var_threshold

        actual_return = returns.iloc[i]

        violation = actual_return < -var

        results.append({
            "DATE": returns.index[i],
            "ACTUAL RETURN": actual_return,
            "VAR": var,
            "VIOLATION": violation,
        })

    return pd.DataFrame(results)


def calculate_violation_statistics(
    backtest_results,
    confidence_level=0.95,
):
    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if "VIOLATION" not in backtest_results.columns:
        raise ValueError(
            "Backtest results must contain a VIOLATION column."
        )

    total_observations = len(backtest_results)

    if total_observations == 0:
        raise ValueError(
            "Backtest results cannot be empty."
        )

    violations = backtest_results["VIOLATION"].sum()

    violation_rate = (
        violations / total_observations
    )

    expected_rate = 1 - confidence_level

    return {
        "total_observations": total_observations,
        "violations": int(violations),
        "violation_rate": violation_rate,
        "expected_rate": expected_rate,
    }