import numpy as np
import pytest

from src.forecasting.lstm_dataset import create_lstm_sequences


def test_sequence_shapes():
    returns = np.arange(100, dtype=float)

    X, y = create_lstm_sequences(
        returns,
        sequence_length=10,
        forecast_horizon=5,
    )

    assert X.shape == (86, 10)
    assert y.shape == (86,)


def test_future_returns_are_not_in_input():
    returns = np.arange(50, dtype=float)

    X, y = create_lstm_sequences(
        returns,
        sequence_length=10,
        forecast_horizon=5,
    )

    assert np.array_equal(X[0], returns[:10])
    assert y[0] == pytest.approx(
        np.std(returns[10:15], ddof=1) * np.sqrt(252)
    )


def test_nan_values_are_removed():
    returns = np.array(
        [0.01, 0.02, np.nan, 0.03, 0.01, 0.02, 0.04, 0.01]
    )

    X, y = create_lstm_sequences(
        returns,
        sequence_length=3,
        forecast_horizon=2,
    )

    assert len(X) == 3
    assert len(y) == 3


def test_invalid_sequence_length():
    returns = np.arange(20, dtype=float)

    with pytest.raises(ValueError):
        create_lstm_sequences(
            returns,
            sequence_length=0,
            forecast_horizon=5,
        )


def test_invalid_forecast_horizon():
    returns = np.arange(20, dtype=float)

    with pytest.raises(ValueError):
        create_lstm_sequences(
            returns,
            sequence_length=5,
            forecast_horizon=1,
        )


def test_insufficient_data():
    returns = np.arange(10, dtype=float)

    with pytest.raises(ValueError):
        create_lstm_sequences(
            returns,
            sequence_length=6,
            forecast_horizon=5,
        )