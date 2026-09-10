import numpy as np
import pandas as pd


def create_volatility_features(returns):
    """
    Create features using only information available up to each day.
    """
    returns = returns.dropna().copy()

    features = pd.DataFrame(index=returns.index)

    features["RETURN"] = returns
    features["ABS_RETURN"] = returns.abs()
    features["SQUARED_RETURN"] = returns ** 2

    # Historical 21-day annualized volatility
    features["ROLLING_VOL"] = (
        returns.rolling(21).std(ddof=1) * np.sqrt(252)
    )

    # EWMA volatility
    lambda_ = 0.94
    ewma_variance = pd.Series(index=returns.index, dtype=float)
    ewma_variance.iloc[0] = returns.var(ddof=1)

    for i in range(1, len(returns)):
        ewma_variance.iloc[i] = (
            lambda_ * ewma_variance.iloc[i - 1]
            + (1 - lambda_) * returns.iloc[i - 1] ** 2
        )

    features["EWMA_VOL"] = np.sqrt(ewma_variance) * np.sqrt(252)

    return features

def create_lstm_sequences(returns, lookback=60, horizon=21):
    if lookback <= 0:
        raise ValueError("lookback must be greater than zero.")

    if horizon <= 1:
        raise ValueError("horizon must be greater than one.")

    returns = returns.dropna().copy()

    features = create_volatility_features(returns)

    sequences = []
    targets = []
    dates = []

    for i in range(lookback - 1, len(features) - horizon):

        # Information available through prediction date t
        history = features.iloc[
            i - lookback + 1:i + 1
        ]

        # Future returns t+1 ... t+horizon
        future_returns = returns.iloc[
            i + 1:i + 1 + horizon
        ]

        target = (
            future_returns.std(ddof=1)
            * np.sqrt(252)
        )

        if history.isna().any().any():
            continue

        sequences.append(
            history.to_numpy(dtype=np.float32)
        )

        targets.append(float(target))
        dates.append(features.index[i])

    X = np.array(
        sequences,
        dtype=np.float32,
    )

    y = np.array(
        targets,
        dtype=np.float32,
    )

    return X, y, pd.DatetimeIndex(dates)