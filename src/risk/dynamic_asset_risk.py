import numpy as np
import pandas as pd


def calculate_dynamic_asset_volatilities(
    asset_returns,
    lambda_=0.94,
):
    """
    Calculate latest annualized EWMA volatility
    for each asset.
    """

    if not isinstance(asset_returns, pd.DataFrame):
        raise ValueError(
            "asset_returns must be a pandas DataFrame."
        )

    if asset_returns.empty:
        raise ValueError(
            "asset_returns cannot be empty."
        )

    if not 0 < lambda_ < 1:
        raise ValueError(
            "lambda_ must be between 0 and 1."
        )

    volatilities = {}

    for asset in asset_returns.columns:

        returns = (
            asset_returns[asset]
            .dropna()
            .astype(float)
        )

        if len(returns) < 2:
            raise ValueError(
                f"Not enough returns for {asset}."
            )

        variance = returns.var(ddof=1)

        for i in range(1, len(returns)):
            variance = (
                lambda_ * variance
                + (1 - lambda_)
                * returns.iloc[i - 1] ** 2
            )

        volatility = (
            np.sqrt(variance)
            * np.sqrt(252)
        )

        volatilities[asset] = volatility

    return pd.Series(
        volatilities,
        dtype=float,
    )