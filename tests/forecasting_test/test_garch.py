import numpy as np
import pandas as pd

from src.forecasting.garch import (
    fit_garch,
    calculate_garch_volatility,
    calculate_annualized_garch_volatility,
    forecast_garch_volatility,
)


def test_fit_garch():

    returns = pd.Series(
        np.random.default_rng(42).normal(0, 0.01, 500)
    )

    result = fit_garch(returns)

    assert result is not None
    assert "omega" in result.params.index
    assert "alpha[1]" in result.params.index
    assert "beta[1]" in result.params.index


def test_garch_volatility():

    returns = pd.Series(
        np.random.default_rng(42).normal(0, 0.01, 500)
    )

    result = fit_garch(returns)

    volatility = calculate_garch_volatility(result)

    assert len(volatility) == len(returns)
    assert np.isfinite(volatility).all()
    assert (volatility > 0).all()


def test_annualized_garch_volatility():

    returns = pd.Series(
        np.random.default_rng(42).normal(0, 0.01, 500)
    )

    result = fit_garch(returns)

    volatility = calculate_annualized_garch_volatility(result)

    assert len(volatility) == len(returns)
    assert np.isfinite(volatility).all()
    assert (volatility > 0).all()


def test_garch_forecast():

    returns = pd.Series(
        np.random.default_rng(42).normal(0, 0.01, 500)
    )

    result = fit_garch(returns)

    forecast = forecast_garch_volatility(result, horizon=5)

    assert len(forecast) == 5
    assert np.isfinite(forecast).all()
    assert (forecast > 0).all()