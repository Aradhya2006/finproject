import numpy as np
import pandas as pd
import pytest

from src.forecasting.evaluation import (
    calculate_forward_realized_volatility,
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
    create_volatility_forecast_dataset,
)


def test_forward_realized_volatility():

    returns = pd.Series(
        np.linspace(
            -0.02,
            0.02,
            30,
        )
    )

    volatility = (
        calculate_forward_realized_volatility(
            returns,
            horizon=5,
        )
    )

    assert len(volatility) == len(returns)

    assert volatility.iloc[:25].notna().all()

    assert volatility.iloc[25:].isna().all()

    assert (
        volatility.dropna() >= 0
    ).all()


def test_invalid_horizon():

    returns = pd.Series(
        [0.01, 0.02, -0.01]
    )

    with pytest.raises(ValueError):
        calculate_forward_realized_volatility(
            returns,
            horizon=1,
        )


def test_mae():

    actual = pd.Series(
        [1.0, 2.0, 3.0]
    )

    predicted = pd.Series(
        [1.5, 1.5, 2.0]
    )

    result = calculate_mae(
        actual,
        predicted,
    )

    expected = (
        abs(1.0 - 1.5)
        + abs(2.0 - 1.5)
        + abs(3.0 - 2.0)
    ) / 3

    assert np.isclose(
        result,
        expected,
    )


def test_rmse():

    actual = pd.Series(
        [1.0, 2.0, 3.0]
    )

    predicted = pd.Series(
        [1.5, 1.5, 2.0]
    )

    result = calculate_rmse(
        actual,
        predicted,
    )

    expected = np.sqrt(
        (
            (1.0 - 1.5) ** 2
            + (2.0 - 1.5) ** 2
            + (3.0 - 2.0) ** 2
        ) / 3
    )

    assert np.isclose(
        result,
        expected,
    )


def test_metrics_require_overlap():

    actual = pd.Series(
        [1.0, 2.0],
        index=[0, 1],
    )

    predicted = pd.Series(
        [3.0, 4.0],
        index=[2, 3],
    )

    with pytest.raises(ValueError):
        calculate_mae(
            actual,
            predicted,
        )

    with pytest.raises(ValueError):
        calculate_rmse(
            actual,
            predicted,
        )


def test_forecast_correlation():

    actual = pd.Series(
        [1.0, 2.0, 3.0]
    )

    predicted = pd.Series(
        [1.0, 2.0, 3.0]
    )

    result = calculate_forecast_correlation(
        actual,
        predicted,
    )

    assert np.isclose(
        result,
        1.0,
    )


def test_create_volatility_forecast_dataset():

    forecast = pd.Series(
        [0.10, 0.20, 0.30],
        index=[0, 1, 2],
    )

    realized = pd.Series(
        [0.12, 0.18, 0.28],
        index=[0, 1, 2],
    )

    result = create_volatility_forecast_dataset(
        forecast,
        realized,
    )

    assert list(result.columns) == [
        "FORECAST",
        "REALIZED",
    ]

    assert len(result) == 3

    assert result.notna().all().all()