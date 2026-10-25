import numpy as np
import pandas as pd
import pytest

from src.forecasting.lstm_dataset import create_lstm_sequences


def test_sequence_shapes():
    returns = pd.Series(
        np.arange(100, dtype=float),
        index=pd.date_range("2020-01-01", periods=100),
    )

    X, y, dates = create_lstm_sequences(
        returns,
        sequence_length=10,
        forecast_horizon=5,
    )

    assert X.shape == (86, 10)
    assert y.shape == (86,)
    assert len(dates) == 86
    assert dates.is_monotonic_increasing


def test_future_returns_are_not_in_input():
    returns = pd.Series(
        np.arange(50, dtype=float),
        index=pd.date_range("2020-01-01", periods=50),
    )

    X, y, dates = create_lstm_sequences(
        returns,
        sequence_length=10,
        forecast_horizon=5,
    )

    assert np.array_equal(
        X[0],
        returns.iloc[:10].to_numpy(),
    )

    assert y[0] == pytest.approx(
        np.std(returns.iloc[10:15], ddof=1) * np.sqrt(252)
    )

    assert dates[0] == returns.index[9]


def test_nan_values_are_removed():
    returns = pd.Series(
        [0.01, 0.02, np.nan, 0.03, 0.01, 0.02, 0.04, 0.01],
        index=pd.date_range("2020-01-01", periods=8),
    )

    X, y, dates = create_lstm_sequences(
        returns,
        sequence_length=3,
        forecast_horizon=2,
    )

    assert len(X) == 3
    assert len(y) == 3
    assert len(dates) == 3


def test_invalid_sequence_length():
    returns = pd.Series(
        np.arange(20, dtype=float),
        index=pd.date_range("2020-01-01", periods=20),
    )

    with pytest.raises(ValueError):
        create_lstm_sequences(
            returns,
            sequence_length=0,
            forecast_horizon=5,
        )


def test_invalid_forecast_horizon():
    returns = pd.Series(
        np.arange(20, dtype=float),
        index=pd.date_range("2020-01-01", periods=20),
    )

    with pytest.raises(ValueError):
        create_lstm_sequences(
            returns,
            sequence_length=5,
            forecast_horizon=1,
        )


def test_insufficient_data():
    returns = pd.Series(
        np.arange(10, dtype=float),
        index=pd.date_range("2020-01-01", periods=10),
    )

    with pytest.raises(ValueError):
        create_lstm_sequences(
            returns,
            sequence_length=6,
            forecast_horizon=5,
        )