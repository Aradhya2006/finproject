import numpy as np
import pandas as pd


def create_forward_realized_volatility(
    returns,
    horizon=21,
):
    """
    Create the common forward realized-volatility target.

    Target at date t:
        volatility of returns t+1 ... t+horizon
        annualized using sqrt(252)
    """
    returns = returns.dropna().copy()

    if horizon <= 1:
        raise ValueError("horizon must be greater than one.")

    realized = pd.Series(
        index=returns.index,
        dtype=float,
        name="REALIZED",
    )

    for i in range(len(returns) - horizon):
        future_returns = returns.iloc[
            i + 1:i + 1 + horizon
        ]

        realized.iloc[i] = (
            future_returns.std(ddof=1)
            * np.sqrt(252)
        )

    return realized


def create_oos_evaluation_dataset(
    returns,
    test_dates,
    horizon=21,
):
    """
    Create the single shared OOS target used by
    all volatility forecasting models.
    """

    realized = create_forward_realized_volatility(
        returns,
        horizon=horizon,
    )

    dataset = pd.DataFrame({
        "REALIZED": realized,
    })

    dataset = dataset.loc[
        dataset.index.isin(test_dates)
    ]

    dataset = dataset.dropna()

    if len(dataset) == 0:
        raise ValueError(
            "No valid OOS observations found."
        )

    return dataset