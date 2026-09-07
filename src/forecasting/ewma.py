import numpy as np
import pandas as pd


def calculate_ewma_variance(
    returns,
    lambda_=0.94,
):
    if not 0 < lambda_ < 1:
        raise ValueError(
            "lambda_ must be between 0 and 1."
        )

    returns = returns.dropna()

    if len(returns) < 2:
        raise ValueError(
            "At least two returns are required."
        )

    variance = pd.Series(
        index=returns.index,
        dtype=float,
    )

    # Initialize using the sample variance
    # of the available returns.
    variance.iloc[0] = returns.var(ddof=1)

    for i in range(1, len(returns)):
        variance.iloc[i] = (
            lambda_ * variance.iloc[i - 1]
            + (1 - lambda_)
            * returns.iloc[i - 1] ** 2
        )

    return variance

def calculate_ewma_volatility(
    returns,
    lambda_=0.94,
):
    variance = calculate_ewma_variance(
        returns,
        lambda_,
    )

    return np.sqrt(variance)


def calculate_annualized_ewma_volatility(
    returns,
    lambda_=0.94,
):
    daily_volatility = calculate_ewma_volatility(
        returns,
        lambda_,
    )

    return daily_volatility * np.sqrt(252)