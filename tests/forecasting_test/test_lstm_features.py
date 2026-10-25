import numpy as np
import pandas as pd
import pytest

from src.forecasting.lstm_features import (
    create_volatility_features,
)


def test_volatility_features():

    returns = pd.Series(
        np.random.default_rng(42).normal(
            0,
            0.01,
            100,
        )
    )

    features = create_volatility_features(
        returns,
        rolling_window=21,
    )

    assert isinstance(
        features,
        pd.DataFrame,
    )

    assert len(features) == len(returns)

    assert list(features.columns) == [
        "RETURN",
        "ABS_RETURN",
        "SQUARED_RETURN",
        "ROLLING_VOLATILITY",
        "EWMA_VOLATILITY",
    ]

    assert np.allclose(
        features["ABS_RETURN"].dropna(),
        np.abs(
            features["RETURN"].dropna()
        ),
    )

    assert np.allclose(
        features["SQUARED_RETURN"].dropna(),
        features["RETURN"].dropna() ** 2,
    )


def test_volatility_features_empty():

    with pytest.raises(ValueError):
        create_volatility_features(
            pd.Series(dtype=float)
        )


def test_volatility_features_wrong_type():

    with pytest.raises(ValueError):
        create_volatility_features(
            np.array([0.01, 0.02])
        )


def test_invalid_rolling_window():

    returns = pd.Series(
        [0.01] * 30
    )

    with pytest.raises(ValueError):
        create_volatility_features(
            returns,
            rolling_window=1,
        )


def test_invalid_lambda():

    returns = pd.Series(
        [0.01] * 30
    )

    with pytest.raises(ValueError):
        create_volatility_features(
            returns,
            ewma_lambda=1.0,
        )