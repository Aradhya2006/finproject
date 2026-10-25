import numpy as np
import pandas as pd
import pytest

from src.forecasting.ewma import (
    calculate_ewma_variance,
    calculate_ewma_volatility,
    calculate_annualized_ewma_volatility,
)


def test_calculate_ewma_variance():

    returns = pd.Series(
        [0.01, -0.02, 0.015, -0.01]
    )

    variance = calculate_ewma_variance(
        returns,
        lambda_=0.94,
    )

    assert len(variance) == len(returns)
    assert variance.notna().all()
    assert (variance >= 0).all()


def test_calculate_ewma_volatility():

    returns = pd.Series(
        [0.01, -0.02, 0.015, -0.01]
    )

    volatility = calculate_ewma_volatility(
        returns,
        lambda_=0.94,
    )

    assert len(volatility) == len(returns)
    assert volatility.notna().all()
    assert (volatility >= 0).all()


def test_annualized_ewma_volatility():

    returns = pd.Series(
        [0.01, -0.02, 0.015, -0.01]
    )

    daily_volatility = calculate_ewma_volatility(
        returns,
        lambda_=0.94,
    )

    annualized_volatility = (
        calculate_annualized_ewma_volatility(
            returns,
            lambda_=0.94,
        )
    )

    expected = daily_volatility * np.sqrt(252)

    pd.testing.assert_series_equal(
        annualized_volatility,
        expected,
    )


def test_invalid_lambda():

    returns = pd.Series(
        [0.01, -0.02, 0.015]
    )

    with pytest.raises(ValueError):
        calculate_ewma_variance(
            returns,
            lambda_=0,
        )

    with pytest.raises(ValueError):
        calculate_ewma_variance(
            returns,
            lambda_=1,
        )


def test_insufficient_data():

    returns = pd.Series([0.01])

    with pytest.raises(ValueError):
        calculate_ewma_variance(
            returns,
            lambda_=0.94,
        )