import numpy as np
import pandas as pd


def create_volatility_features(
    returns,
    rolling_window=21,
    ewma_lambda=0.94,
):
    if not isinstance(returns, pd.Series):
        raise ValueError(
            "returns must be a pandas Series."
        )

    if returns.empty:
        raise ValueError(
            "returns cannot be empty."
        )

    if rolling_window <= 1:
        raise ValueError(
            "rolling_window must be greater than 1."
        )

    if not 0 < ewma_lambda < 1:
        raise ValueError(
            "ewma_lambda must be between 0 and 1."
        )

    clean_returns = returns.dropna().astype(float)

    features = pd.DataFrame(
        index=clean_returns.index
    )

    # Raw return
    features["RETURN"] = clean_returns

    # Absolute return
    features["ABS_RETURN"] = np.abs(
        clean_returns
    )

    # Squared return
    features["SQUARED_RETURN"] = (
        clean_returns ** 2
    )

    # Rolling annualized volatility
    features["ROLLING_VOLATILITY"] = (
        clean_returns
        .rolling(rolling_window)
        .std()
        * np.sqrt(252)
    )

    # EWMA variance
    ewma_variance = pd.Series(
        index=clean_returns.index,
        dtype=float,
    )

    ewma_variance.iloc[0] = (
        clean_returns.var(ddof=1)
    )

    for i in range(1, len(clean_returns)):
        ewma_variance.iloc[i] = (
            ewma_lambda
            * ewma_variance.iloc[i - 1]
            + (1 - ewma_lambda)
            * clean_returns.iloc[i - 1] ** 2
        )

    features["EWMA_VOLATILITY"] = (
        np.sqrt(ewma_variance)
        * np.sqrt(252)
    )

    return features