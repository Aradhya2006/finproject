import numpy as np
import pandas as pd
from arch import arch_model


def fit_garch(returns, p=1, q=1, dist="normal"):
    """
    Fit a GARCH(p,q) model to return data.

    Parameters
    ----------
    returns : pd.Series
        Daily returns in decimal form.
    p : int
        Number of lagged squared shocks.
    q : int
        Number of lagged conditional variances.
    dist : str
        Distribution of standardized residuals.

    Returns
    -------
    result
        Fitted ARCH/GARCH model result.
    """

    if p < 1 or q < 1:
        raise ValueError("p and q must be greater than or equal to 1.")

    clean_returns = returns.dropna()

    if len(clean_returns) < 100:
        raise ValueError("At least 100 returns are required.")

    # Convert decimal returns to percentage returns.
    # This improves numerical stability during optimization.
    scaled_returns = clean_returns * 100

    model = arch_model(
        scaled_returns,
        mean="Constant",
        vol="GARCH",
        p=p,
        q=q,
        dist=dist,
        rescale=False,
    )

    result = model.fit(disp="off")

    return result


def calculate_garch_volatility(result):
    """
    Return conditional daily volatility in decimal form.
    """

    volatility = result.conditional_volatility / 100

    return volatility


def calculate_annualized_garch_volatility(result):
    """
    Return annualized conditional volatility.
    """

    daily_volatility = calculate_garch_volatility(result)

    return daily_volatility * np.sqrt(252)


def forecast_garch_volatility(result, horizon=1):
    """
    Forecast future volatility from the fitted GARCH model.

    Returns
    -------
    pd.Series
        Forecasted daily volatility in decimal form.
    """

    if horizon < 1:
        raise ValueError("horizon must be at least 1.")

    forecast = result.forecast(horizon=horizon)

    variance = forecast.variance.iloc[-1]

    volatility = np.sqrt(variance) / 100

    volatility.index = range(1, horizon + 1)

    return volatility