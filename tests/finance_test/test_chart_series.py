import numpy as np
import pandas as pd
import pytest

from src.risk.chart_series import (
    monte_carlo_fan,
    portfolio_value_series,
    rebase_to,
    risk_series,
    to_json_list,
    value_histogram,
)


def _dates(n, start="2024-01-01"):
    return pd.bdate_range(start, periods=n)


def test_portfolio_value_is_shares_times_close():
    prices = pd.DataFrame({
        "DATE": _dates(3),
        "TCS": [100.0, 110.0, 120.0],
        "INFY": [50.0, 45.0, 60.0],
    })

    value = portfolio_value_series(prices, {"TCS": 2, "INFY": 4})

    assert value.tolist() == [2 * 100 + 4 * 50, 2 * 110 + 4 * 45, 2 * 120 + 4 * 60]


def test_rebase_scales_to_start_value_and_keeps_gaps():
    series = pd.Series([np.nan, 50.0, 100.0], index=_dates(3))

    rebased = rebase_to(series, 1000.0)

    assert np.isnan(rebased.iloc[0])
    assert rebased.iloc[1] == 1000.0
    assert rebased.iloc[2] == 2000.0


def test_risk_series_uses_only_past_data():
    rng = np.random.default_rng(3)
    returns = pd.Series(rng.normal(0, 0.01, 400), index=_dates(400))

    frame = risk_series(returns, window=100)

    # Thresholds are not scored during the seed window.
    assert frame["VAR_EWMA"].iloc[:100].isna().all()
    assert frame["VAR_EWMA"].iloc[100:].notna().all()

    # Changing a future return must not change an earlier threshold.
    changed = returns.copy()
    changed.iloc[350] = -0.5
    later = risk_series(changed, window=100)
    assert later["VAR_EWMA"].iloc[:300].equals(frame["VAR_EWMA"].iloc[:300])
    assert later["VAR_HISTORICAL"].iloc[:300].equals(frame["VAR_HISTORICAL"].iloc[:300])


def test_ewma_threshold_is_about_1_645_sigma_for_normal_returns():
    rng = np.random.default_rng(4)
    returns = pd.Series(rng.normal(0, 0.01, 2000), index=_dates(2000))

    frame = risk_series(returns, window=252)
    scored = frame.dropna()

    breach_rate = scored["BREACH"].mean()
    assert 0.02 < breach_rate < 0.08  # roughly 5% for a well-specified model


def test_risk_series_rejects_short_history():
    with pytest.raises(ValueError):
        risk_series(pd.Series([0.01] * 10, index=_dates(10)), window=252)


def test_monte_carlo_fan_starts_at_value_and_orders_percentiles():
    rng = np.random.default_rng(5)
    simulated = rng.normal(0.0005, 0.01, size=(500, 21))

    fan = monte_carlo_fan(simulated, start_value=1000.0)

    assert len(fan["days"]) == 22
    assert fan["p50"][0] == 1000.0
    for day in range(22):
        assert fan["p05"][day] <= fan["p25"][day] <= fan["p50"][day] <= fan["p75"][day] <= fan["p95"][day]


def test_histogram_counts_every_simulation():
    values = np.linspace(0, 100, 1000)

    bins = value_histogram(values, bins=10)

    assert len(bins) == 10
    assert sum(b["count"] for b in bins) == 1000
    assert bins[0]["low"] == pytest.approx(0)
    assert bins[-1]["high"] == pytest.approx(100)


def test_to_json_list_maps_nan_to_none():
    out = to_json_list([1.5, np.nan, np.bool_(True)])

    assert out == [1.5, None, True]
