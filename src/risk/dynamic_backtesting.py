import numpy as np
import pandas as pd


def backtest_dynamic_ewma_var(
    asset_returns,
    weights,
    confidence_level=0.95,
    lambda_=0.94,
    window=252,
):
    """
    Backtest one-day dynamic parametric VaR.

    At each test date, only the previous `window`
    trading days are used to estimate:

    1. EWMA volatility for each asset
    2. Correlation between assets

    The resulting covariance matrix is then used
    to forecast portfolio volatility and VaR.

    No future information is used.
    """

    if not isinstance(asset_returns, pd.DataFrame):
        raise ValueError(
            "asset_returns must be a pandas DataFrame."
        )

    if asset_returns.empty:
        raise ValueError(
            "asset_returns cannot be empty."
        )

    if window <= 1:
        raise ValueError(
            "window must be greater than 1."
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if not 0 < lambda_ < 1:
        raise ValueError(
            "lambda_ must be between 0 and 1."
        )

    assets = list(weights.keys())

    missing_assets = [
        asset
        for asset in assets
        if asset not in asset_returns.columns
    ]

    if missing_assets:
        raise ValueError(
            f"Missing assets: {missing_assets}"
        )

    returns = (
        asset_returns[assets]
        .dropna()
        .sort_index()
    )

    z_scores = {
        0.90: -1.2815515655446004,
        0.95: -1.6448536269514729,
        0.99: -2.3263478740408408,
    }

    if confidence_level not in z_scores:
        raise ValueError(
            "Unsupported confidence level."
        )

    z = z_scores[confidence_level]

    weight_vector = np.array(
        [
            weights[asset]
            for asset in assets
        ]
    )

    results = []

    for i in range(window, len(returns)):

        # --------------------------------------------------
        # Information available BEFORE test date i
        # --------------------------------------------------

        historical_returns = returns.iloc[
            i - window:i
        ]

        # --------------------------------------------------
        # EWMA asset volatility
        # --------------------------------------------------

        forecast_volatilities = {}

        for asset in assets:

            series = historical_returns[asset]

            variance = series.var(ddof=1)

            for j in range(1, len(series)):
                variance = (
                    lambda_ * variance
                    + (1 - lambda_)
                    * series.iloc[j - 1] ** 2
                )

            forecast_volatilities[asset] = (
                np.sqrt(variance)
                * np.sqrt(252)
            )

        forecast_volatilities = pd.Series(
            forecast_volatilities
        )

        # --------------------------------------------------
        # Point-in-time correlation
        # --------------------------------------------------

        correlation_matrix = (
            historical_returns
            .corr()
            .loc[assets, assets]
        )

        volatility_vector = (
            forecast_volatilities
            .to_numpy()
        )

        correlation = (
            correlation_matrix
            .to_numpy()
        )

        covariance = (
            np.outer(
                volatility_vector,
                volatility_vector,
            )
            * correlation
        )

        # --------------------------------------------------
        # Portfolio volatility
        # --------------------------------------------------

        portfolio_variance = (
            weight_vector.T
            @ covariance
            @ weight_vector
        )

        if portfolio_variance < 0:
            raise ValueError(
                "Portfolio variance cannot be negative."
            )

        portfolio_volatility = np.sqrt(
            portfolio_variance
        )

        # --------------------------------------------------
        # One-day parametric VaR
        # --------------------------------------------------

        daily_volatility = (
            portfolio_volatility
            / np.sqrt(252)
        )

        var_return = (
            z * daily_volatility
        )

        # --------------------------------------------------
        # Actual return on test date
        # --------------------------------------------------

        actual_return = (
            weight_vector
            @ returns.iloc[i].to_numpy()
        )

        violation = (
            actual_return < var_return
        )

        results.append(
            {
                "DATE": returns.index[i],
                "ACTUAL RETURN": actual_return,
                "VAR RETURN": -var_return,
                "VIOLATION": violation,
                "FORECAST VOLATILITY":
                    portfolio_volatility,
            }
        )

    return pd.DataFrame(results)