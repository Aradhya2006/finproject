import numpy as np
import pandas as pd


def calculate_dynamic_covariance(
    forecast_volatilities,
    correlation_matrix,
):
    """
    Build a forward-looking covariance matrix from
    forecasted asset volatilities and a correlation matrix.

    Parameters
    ----------
    forecast_volatilities : pd.Series
        Forecasted annualized volatility for each asset.

    correlation_matrix : pd.DataFrame
        Correlation matrix for the same assets.

    Returns
    -------
    pd.DataFrame
        Dynamic annualized covariance matrix.
    """

    if not isinstance(
        forecast_volatilities,
        pd.Series,
    ):
        raise ValueError(
            "forecast_volatilities must be a pandas Series."
        )

    if not isinstance(
        correlation_matrix,
        pd.DataFrame,
    ):
        raise ValueError(
            "correlation_matrix must be a pandas DataFrame."
        )

    if forecast_volatilities.empty:
        raise ValueError(
            "forecast_volatilities cannot be empty."
        )

    if correlation_matrix.empty:
        raise ValueError(
            "correlation_matrix cannot be empty."
        )

    assets = list(forecast_volatilities.index)

    if list(correlation_matrix.index) != assets:
        raise ValueError(
            "Correlation matrix index does not match assets."
        )

    if list(correlation_matrix.columns) != assets:
        raise ValueError(
            "Correlation matrix columns do not match assets."
        )

    if not np.all(
        np.isfinite(
            forecast_volatilities.to_numpy()
        )
    ):
        raise ValueError(
            "Forecast volatilities must be finite."
        )

    if (forecast_volatilities <= 0).any():
        raise ValueError(
            "Forecast volatilities must be positive."
        )

    if not np.all(
        np.isfinite(
            correlation_matrix.to_numpy()
        )
    ):
        raise ValueError(
            "Correlation matrix must contain finite values."
        )

    volatility_vector = (
        forecast_volatilities.to_numpy()
    )

    correlation = (
        correlation_matrix.to_numpy()
    )

    covariance = (
        np.outer(
            volatility_vector,
            volatility_vector,
        )
        * correlation
    )

    return pd.DataFrame(
        covariance,
        index=assets,
        columns=assets,
    )


def calculate_dynamic_portfolio_volatility(
    weights,
    forecast_volatilities,
    correlation_matrix,
):
    """
    Calculate forward-looking annualized
    portfolio volatility.
    """

    covariance_matrix = (
        calculate_dynamic_covariance(
            forecast_volatilities,
            correlation_matrix,
        )
    )

    weight_vector = np.array(
        [
            weights[asset]
            for asset in covariance_matrix.columns
        ]
    )

    covariance = covariance_matrix.to_numpy()

    portfolio_variance = (
        weight_vector.T
        @ covariance
        @ weight_vector
    )

    if portfolio_variance < 0:
        raise ValueError(
            "Portfolio variance cannot be negative."
        )

    return np.sqrt(portfolio_variance)