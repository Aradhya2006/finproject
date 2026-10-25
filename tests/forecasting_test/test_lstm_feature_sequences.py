import numpy as np
import pandas as pd
import pytest

from src.forecasting.lstm_dataset import (
    create_lstm_feature_sequences,
)


def test_create_lstm_feature_sequences():

    rng = np.random.default_rng(42)

    dates = pd.date_range(
        "2020-01-01",
        periods=120,
        freq="D",
    )

    features = pd.DataFrame(
        rng.normal(
            0,
            1,
            size=(120, 5),
        ),
        index=dates,
        columns=[
            "RETURN",
            "ABS_RETURN",
            "SQUARED_RETURN",
            "ROLLING_VOLATILITY",
            "EWMA_VOLATILITY",
        ],
    )

    returns = pd.Series(
        rng.normal(
            0,
            0.01,
            120,
        ),
        index=dates,
    )

    X, y, sequence_dates = (
        create_lstm_feature_sequences(
            features,
            returns,
            sequence_length=60,
            forecast_horizon=21,
        )
    )

    expected_samples = (
        120 - 60 - 21 + 1
    )

    assert X.shape == (
        expected_samples,
        60,
        5,
    )

    assert y.shape == (
        expected_samples,
    )

    assert len(sequence_dates) == (
        expected_samples
    )

    assert np.all(
        np.isfinite(X)
    )

    assert np.all(
        np.isfinite(y)
    )


def test_nan_feature_rows_are_removed():

    rng = np.random.default_rng(42)

    dates = pd.date_range(
        "2020-01-01",
        periods=100,
        freq="D",
    )

    features = pd.DataFrame(
        rng.normal(
            0,
            1,
            size=(100, 5),
        ),
        index=dates,
        columns=[
            "RETURN",
            "ABS_RETURN",
            "SQUARED_RETURN",
            "ROLLING_VOLATILITY",
            "EWMA_VOLATILITY",
        ],
    )

    features.iloc[:10, 3] = np.nan

    returns = pd.Series(
        rng.normal(
            0,
            0.01,
            100,
        ),
        index=dates,
    )

    X, y, dates_out = (
        create_lstm_feature_sequences(
            features,
            returns,
            sequence_length=20,
            forecast_horizon=10,
        )
    )

    assert X.shape[1:] == (
        20,
        5,
    )

    assert len(X) == len(y)
    assert len(X) == len(dates_out)


def test_mismatched_indexes():

    features = pd.DataFrame(
        [[1, 2, 3, 4, 5]],
        index=pd.date_range(
            "2020-01-01",
            periods=1,
        ),
    )

    returns = pd.Series(
        [0.01],
        index=pd.date_range(
            "2020-01-02",
            periods=1,
        ),
    )

    with pytest.raises(ValueError):
        create_lstm_feature_sequences(
            features,
            returns,
        )