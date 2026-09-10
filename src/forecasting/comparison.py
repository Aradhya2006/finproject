import numpy as np
import pandas as pd

from src.risk.regime import (
    calculate_rolling_volatility,
)

from src.forecasting.ewma import (
    calculate_ewma_variance,
)

from src.forecasting.evaluation import (
    calculate_forward_realized_volatility,
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
)
def compare_volatility_forecasts(
    returns,
    evaluation_start,
    evaluation_end,
    rolling_window=21,
    ewma_lambda=0.94,
    realized_horizon=21,
):
    """
    Compare volatility forecasts over a common
    out-of-sample evaluation period.

    Target:
        Next `realized_horizon` trading days'
        annualized realized volatility.

    Forecasts:
        Rolling volatility
        EWMA volatility
    """

    if not isinstance(returns, pd.Series):
        raise ValueError(
            "returns must be a pandas Series."
        )

    returns = returns.dropna().astype(float)

    # -----------------------------------------
    # Realized future volatility
    # -----------------------------------------

    realized = calculate_forward_realized_volatility(
        returns,
        horizon=realized_horizon,
    )

    # -----------------------------------------
    # Rolling volatility
    # -----------------------------------------

    rolling = calculate_rolling_volatility(
        returns,
        window=rolling_window,
    )

    # -----------------------------------------
    # EWMA volatility
    # -----------------------------------------

    ewma_variance = calculate_ewma_variance(
        returns,
        lambda_=ewma_lambda,
    )

    ewma = np.sqrt(
        ewma_variance
    ) * np.sqrt(252)

    # -----------------------------------------
    # Combine
    # -----------------------------------------

    comparison = pd.DataFrame({
        "REALIZED": realized,
        "ROLLING": rolling,
        "EWMA": ewma,
    })

    # Only evaluate dates where every model
    # has both a forecast and future target.
    comparison = comparison.dropna()

    comparison = comparison.loc[
        evaluation_start:evaluation_end
    ]

    if comparison.empty:
        raise ValueError(
            "No observations available for "
            "the requested evaluation period."
        )

    # -----------------------------------------
    # Metrics
    # -----------------------------------------

    results = {}

    for model_name in [
        "ROLLING",
        "EWMA",
    ]:

        predictions = comparison[model_name]

        actual = comparison["REALIZED"]

        results[model_name] = {
            "OBS": len(comparison),
            "MAE": calculate_mae(
                predictions,
                actual,
            ),
            "RMSE": calculate_rmse(
                predictions,
                actual,
            ),
            "CORR": calculate_forecast_correlation(
                predictions,
                actual,
            ),
            "AVG FORECAST": np.mean(
                predictions
            ),
            "AVG REALIZED": np.mean(
                actual
            ),
        }

    return comparison, results