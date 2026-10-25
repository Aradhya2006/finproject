import numpy as np
import pytest

from src.forecasting.lstm_evaluation import (
    calculate_lstm_metrics,
)


def test_lstm_metrics():

    predictions = np.array(
        [0.20, 0.25, 0.30]
    )

    actual = np.array(
        [0.22, 0.23, 0.32]
    )

    metrics = calculate_lstm_metrics(
        predictions,
        actual,
    )

    assert "MAE" in metrics
    assert "RMSE" in metrics
    assert "CORR" in metrics

    assert metrics["MAE"] >= 0
    assert metrics["RMSE"] >= 0

    assert np.isfinite(metrics["MAE"])
    assert np.isfinite(metrics["RMSE"])
    assert np.isfinite(metrics["CORR"])


def test_lstm_metrics_mismatched_lengths():

    predictions = np.array(
        [0.20, 0.25]
    )

    actual = np.array(
        [0.22, 0.23, 0.32]
    )

    with pytest.raises(ValueError):
        calculate_lstm_metrics(
            predictions,
            actual,
        )


def test_lstm_metrics_empty():

    with pytest.raises(ValueError):
        calculate_lstm_metrics(
            np.array([]),
            np.array([]),
        )


def test_lstm_metrics_non_finite():

    predictions = np.array(
        [0.20, np.nan, 0.30]
    )

    actual = np.array(
        [0.22, 0.23, 0.32]
    )

    with pytest.raises(ValueError):
        calculate_lstm_metrics(
            predictions,
            actual,
        )