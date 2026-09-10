import numpy as np
import pandas as pd

from src.forecasting.evaluation_dataset import (
    create_oos_evaluation_dataset,
)
from src.forecasting.ewma import calculate_ewma_volatility
from src.forecasting.evaluation import (
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
)
from src.forecasting.rolling import calculate_rolling_volatility_forecast


def calculate_forward_realized_volatility(returns, horizon=21):
    """
    Calculate annualized realized volatility over the next
    `horizon` trading days.
    """
    returns = returns.dropna()

    realized = pd.Series(
        index=returns.index,
        dtype=float,
    )

    for i in range(len(returns) - horizon):
        future_returns = returns.iloc[i + 1:i + 1 + horizon]

        realized.iloc[i] = (
            future_returns.std(ddof=1) * np.sqrt(252)
        )

    return realized


def evaluate_baseline_models(
    returns,
    test_dates,
    rolling_window=21,
    ewma_lambda=0.94,
    horizon=21,
):
    """
    Evaluate Rolling and EWMA volatility forecasts on
    the exact same OOS dates used by the LSTM.
    """

    returns = returns.dropna().copy()

    evaluation_dataset = create_oos_evaluation_dataset(
    returns,
    test_dates,
    horizon=horizon,
)

    realized = evaluation_dataset["REALIZED"]

    rolling = calculate_rolling_volatility_forecast(
        returns,
        window=rolling_window,
    )

    ewma = (
        calculate_ewma_volatility(
            returns,
            lambda_=ewma_lambda,
        )
        * np.sqrt(252)
    )

    comparison = pd.DataFrame({
        "REALIZED": realized,
        "ROLLING": rolling,
        "EWMA": ewma,
    })

    comparison = comparison.loc[
        comparison.index.isin(test_dates)
    ]

    comparison = comparison.dropna()

    results = {}

    for model in ["ROLLING", "EWMA"]:

        results[model] = {
            "observations": len(comparison),

            "mae": calculate_mae(
                comparison["REALIZED"],
                comparison[model],
            ),

            "rmse": calculate_rmse(
                comparison["REALIZED"],
                comparison[model],
            ),

            "correlation": calculate_forecast_correlation(
                comparison["REALIZED"],
                comparison[model],
            ),

            "average_forecast": float(
                comparison[model].mean()
            ),

            "average_realized": float(
                comparison["REALIZED"].mean()
            ),
        }

    return comparison, results