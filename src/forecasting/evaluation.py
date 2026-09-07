import numpy as np
import pandas as pd


def calculate_forward_realized_volatility(
    returns,
    horizon=21,
):
    if horizon <= 1:
        raise ValueError(
            "horizon must be greater than 1."
        )

    returns = returns.dropna()

    if len(returns) <= horizon:
        raise ValueError(
            "Not enough returns for the selected horizon."
        )

    realized_volatility = pd.Series(
        index=returns.index,
        dtype=float,
    )

    for i in range(len(returns) - horizon):
        future_returns = returns.iloc[
            i + 1 : i + 1 + horizon
        ]

        realized_volatility.iloc[i] = (
            future_returns.std(ddof=1)
            * np.sqrt(252)
        )

    return realized_volatility


def calculate_mae(
    actual,
    predicted,
):
    aligned = pd.concat(
        [actual, predicted],
        axis=1,
    ).dropna()

    if len(aligned) == 0:
        raise ValueError(
            "No overlapping observations."
        )

    return np.mean(
        np.abs(
            aligned.iloc[:, 0]
            - aligned.iloc[:, 1]
        )
    )


def calculate_rmse(
    actual,
    predicted,
):
    aligned = pd.concat(
        [actual, predicted],
        axis=1,
    ).dropna()

    if len(aligned) == 0:
        raise ValueError(
            "No overlapping observations."
        )

    return np.sqrt(
        np.mean(
            (
                aligned.iloc[:, 0]
                - aligned.iloc[:, 1]
            ) ** 2
        )
    )




def create_volatility_forecast_dataset(
    ewma_volatility,
    realized_volatility,
):
    data = pd.concat(
        [
            ewma_volatility.rename("FORECAST"),
            realized_volatility.rename("REALIZED"),
        ],
        axis=1,
    )

    data = data.dropna()

    if len(data) == 0:
        raise ValueError(
            "No overlapping forecast and realized observations."
        )

    return data


def calculate_forecast_correlation(
    actual,
    predicted,
):
    aligned = pd.concat(
        [actual, predicted],
        axis=1,
    ).dropna()

    if len(aligned) < 2:
        raise ValueError(
            "At least two overlapping observations are required."
        )

    return aligned.iloc[:, 0].corr(
        aligned.iloc[:, 1]
    )




def calculate_forecast_correlation(
    actual,
    predicted,
):
    aligned = pd.concat(
        [actual, predicted],
        axis=1,
    ).dropna()

    if len(aligned) < 2:
        raise ValueError(
            "At least two overlapping observations are required."
        )

    return aligned.iloc[:, 0].corr(
        aligned.iloc[:, 1]
    )


def create_volatility_forecast_dataset(
    forecast,
    realized_volatility,
):
    data = pd.concat(
        [
            forecast.rename("FORECAST"),
            realized_volatility.rename("REALIZED"),
        ],
        axis=1,
    )

    data = data.dropna()

    if len(data) == 0:
        raise ValueError(
            "No overlapping forecast and realized observations."
        )

    return data