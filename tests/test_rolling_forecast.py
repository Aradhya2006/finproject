import numpy as np
import pandas as pd
import pytest

from src.forecasting.rolling import (
    calculate_rolling_volatility_forecast,
)


def test_rolling_volatility_forecast():

    returns = pd.Series(
        [
            0.01,
            -0.02,
            0.015,
            -0.01,
            0.005,
        ]
    )

    result = calculate_rolling_volatility_forecast(
        returns,
        window=3,
    )

    assert len(result) == len(returns)

    assert result.iloc[:2].isna().all()

    assert result.iloc[2:].notna().all()

    assert (
        result.dropna() >= 0
    ).all()


def test_rolling_volatility_matches_manual_calculation():

    returns = pd.Series(
        [
            0.01,
            -0.02,
            0.015,
        ]
    )

    result = calculate_rolling_volatility_forecast(
        returns,
        window=3,
    )

    expected = (
        returns.std(ddof=1)
        * np.sqrt(252)
    )

    assert np.isclose(
        result.iloc[-1],
        expected,
    )


def test_invalid_window():

    returns = pd.Series(
        [0.01, -0.02, 0.015]
    )

    with pytest.raises(ValueError):
        calculate_rolling_volatility_forecast(
            returns,
            window=1,
        )


def test_insufficient_data():

    returns = pd.Series(
        [0.01, -0.02]
    )

    with pytest.raises(ValueError):
        calculate_rolling_volatility_forecast(
            returns,
            window=3,
        )