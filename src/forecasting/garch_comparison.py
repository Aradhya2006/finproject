import numpy as np
import pandas as pd

from src.forecasting.garch import fit_garch
from src.forecasting.garch import forecast_garch_volatility
from src.forecasting.evaluation import (
    calculate_forward_realized_volatility,
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
)


def evaluate_garch_common_period(
    returns,
    evaluation_start,
    evaluation_end,
    realized_horizon=21,
    refit_frequency=21,
):
    if not isinstance(returns, pd.Series):
        raise ValueError(
            "returns must be a pandas Series."
        )

    returns = returns.dropna().astype(float)

    realized = calculate_forward_realized_volatility(
        returns,
        horizon=realized_horizon,
    )

    evaluation_dates = realized.loc[
        evaluation_start:evaluation_end
    ].index

    if len(evaluation_dates) == 0:
        raise ValueError(
            "No evaluation dates available."
        )

    forecasts = []

    last_fit_position = -refit_frequency
    current_result = None

    for date in evaluation_dates:

        date_position = returns.index.get_loc(
            date
        )

        if (
            current_result is None
            or date_position - last_fit_position
            >= refit_frequency
        ):

            historical_returns = returns.iloc[
                :date_position + 1
            ]

            current_result = fit_garch(
                historical_returns,
                p=1,
                q=1,
                dist="normal",
            )

            last_fit_position = date_position

        forecast = forecast_garch_volatility(
    current_result,
    horizon=1,
)

        annualized_forecast = (
    forecast.iloc[0] * np.sqrt(252)
)

        forecasts.append(
    annualized_forecast
)

    comparison = pd.DataFrame(
        {
            "GARCH": forecasts,
            "REALIZED": realized.loc[
                evaluation_dates
            ].to_numpy(),
        },
        index=evaluation_dates,
    )

    comparison = comparison.dropna()

    results = {
        "OBS": len(comparison),
        "MAE": calculate_mae(
            comparison["GARCH"],
            comparison["REALIZED"],
        ),
        "RMSE": calculate_rmse(
            comparison["GARCH"],
            comparison["REALIZED"],
        ),
        "CORR": calculate_forecast_correlation(
            comparison["GARCH"],
            comparison["REALIZED"],
        ),
        "AVG FORECAST": comparison[
            "GARCH"
        ].mean(),
        "AVG REALIZED": comparison[
            "REALIZED"
        ].mean(),
    }

    return comparison, results