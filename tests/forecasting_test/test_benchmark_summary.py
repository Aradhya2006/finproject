import numpy as np
import pandas as pd
import pytest

from src.forecasting.benchmark_summary import (
    benchmark_summary,
    directional_accuracy,
    rank_correlation,
    volatility_regimes,
)


def test_directional_accuracy_counts_matching_moves():
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    realized = pd.Series([0.10, 0.20, 0.15, 0.18, 0.12], index=dates)  # moves: up, down, up, down
    forecast = pd.Series([0.10, 0.25, 0.14, 0.19, 0.20], index=dates)  # moves: up, down, down, up

    # Three of the four day-over-day moves agree; the third day does not.
    assert directional_accuracy(realized, forecast) == pytest.approx(3 / 4)


def test_directional_accuracy_is_none_without_enough_days():
    dates = pd.date_range("2026-01-01", periods=1, freq="D")

    assert directional_accuracy(pd.Series([0.1], index=dates), pd.Series([0.1], index=dates)) is None


def test_rank_correlation_is_one_for_matching_order():
    values = pd.Series([0.1, 0.2, 0.3, 0.4])

    assert rank_correlation(values, values * 10) == pytest.approx(1.0)


def test_volatility_regimes_shares_add_to_one():
    rng = np.random.default_rng(1)
    returns = pd.Series(rng.normal(0, 0.012, 600))

    regimes = volatility_regimes(returns)

    assert sum(regimes["shares"].values()) == pytest.approx(1.0)
    assert regimes["current"] in {"low", "normal", "high"}


def test_volatility_regimes_stay_probability_is_one_when_band_never_changes():
    # Calm, constant returns stay in the low band for every day.
    returns = pd.Series([0.001, -0.001] * 200)

    regimes = volatility_regimes(returns)

    assert regimes["shares"]["low"] == pytest.approx(1.0)
    assert regimes["stay"]["low"] == pytest.approx(1.0)
    assert regimes["stay"]["high"] is None  # no day was ever in the high band


def test_benchmark_summary_reports_garch_gap_against_lstm():
    dates = pd.date_range("2026-01-01", periods=6, freq="D")
    chart_frame = pd.DataFrame(
        {
            "REALIZED": [0.20, 0.22, 0.21, 0.25, 0.24, 0.23],
            "ROLLING": [0.20] * 6,
            "EWMA": [0.19, 0.21, 0.20, 0.24, 0.23, 0.22],
            "garch": [0.20, 0.22, 0.21, 0.25, 0.24, 0.23],
            "lstm": [0.21, 0.22, 0.20, 0.24, 0.25, 0.22],
        },
        index=dates,
    )

    summary = benchmark_summary(
        chart_frame,
        garch_results={"rmse": 0.022},
        lstm_results={"rmse": 0.020},
    )

    # GARCH is 10% above LSTM here.
    assert summary["garch_rmse_vs_lstm_pct"] == pytest.approx(10.0)
    assert summary["latest_ewma"] == pytest.approx(0.22)
    assert set(summary["directional_accuracy"]) == {"rolling", "ewma", "garch", "lstm"}
