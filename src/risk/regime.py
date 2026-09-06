import numpy as np
import pandas as pd


def calculate_rolling_volatility(
    portfolio_returns,
    window=21,
):
    returns = portfolio_returns.dropna()

    if window <= 1:
        raise ValueError("window must be greater than 1.")

    if len(returns) < window:
        raise ValueError(
            "Not enough returns for the selected window."
        )

    rolling_volatility = (
        returns
        .rolling(window)
        .std()
        * np.sqrt(252)
    )

    return rolling_volatility




def classify_volatility_regimes(
    rolling_volatility,
):
    volatility = rolling_volatility.dropna()

    if len(volatility) < 3:
        raise ValueError(
            "Not enough observations to classify regimes."
        )

    low_threshold = volatility.quantile(1 / 3)
    high_threshold = volatility.quantile(2 / 3)

    regimes = pd.Series(
        index=volatility.index,
        dtype="object",
    )

    regimes[volatility <= low_threshold] = "LOW"
    regimes[
        (volatility > low_threshold)
        & (volatility <= high_threshold)
    ] = "NORMAL"
    regimes[volatility > high_threshold] = "HIGH"

    return regimes