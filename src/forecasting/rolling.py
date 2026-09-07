import numpy as np
import pandas as pd


def calculate_rolling_volatility_forecast(
    returns,
    window=21,
):
    if window <= 1:
        raise ValueError(
            "window must be greater than 1."
        )

    returns = returns.dropna()

    if len(returns) < window:
        raise ValueError(
            "Not enough returns for the selected window."
        )

    volatility = (
        returns
        .rolling(window)
        .std(ddof=1)
        * np.sqrt(252)
    )

    return volatility