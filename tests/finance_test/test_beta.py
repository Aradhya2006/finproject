import numpy as np
import pandas as pd

from src.finance.beta import calculate_beta


def _series(values, start="2024-01-01"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)))


def test_beta_recovers_known_slope():
    rng = np.random.default_rng(0)
    benchmark = rng.normal(0, 0.01, 500)
    portfolio = 1.5 * benchmark + rng.normal(0, 0.0005, 500)

    beta = calculate_beta(_series(portfolio), _series(benchmark))

    assert beta is not None
    assert abs(beta - 1.5) < 0.05


def test_beta_uses_only_overlapping_dates():
    rng = np.random.default_rng(1)
    benchmark = _series(rng.normal(0, 0.01, 300))
    # The portfolio only has history for the last 200 benchmark dates.
    portfolio = 2.0 * benchmark.iloc[100:]

    beta = calculate_beta(portfolio, benchmark)

    assert beta is not None
    assert abs(beta - 2.0) < 1e-9


def test_beta_is_none_without_enough_observations():
    returns = _series(np.linspace(-0.01, 0.01, 10))

    assert calculate_beta(returns, returns) is None


def test_beta_is_none_for_flat_benchmark():
    portfolio = _series(np.random.default_rng(2).normal(0, 0.01, 100))
    flat = _series(np.zeros(100))

    assert calculate_beta(portfolio, flat) is None
