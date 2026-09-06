import numpy as np


def calculate_historical_cvar(
    portfolio_returns,
    confidence_level=0.95,
):
    returns = portfolio_returns.dropna()

    tail_probability = 1 - confidence_level

    var_threshold = np.percentile(
        returns,
        tail_probability * 100,
    )

    tail_returns = returns[
        returns <= var_threshold
    ]

    cvar = -np.mean(tail_returns)

    return cvar