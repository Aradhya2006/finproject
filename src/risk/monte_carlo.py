import numpy as np
import pandas as pd


def simulate_asset_returns(
    forecast_volatilities,
    correlation_matrix,
    simulations=10000,
    horizon=21,
    seed=42,
):
    """
    Simulate correlated daily returns for each portfolio asset.

    Parameters
    ----------
    forecast_volatilities : pd.Series
        Annualized volatility for each asset.

    correlation_matrix : pd.DataFrame
        Correlation matrix between assets.

    simulations : int
        Number of simulated paths.

    horizon : int
        Number of future trading days.

    seed : int
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Shape: (simulations, horizon, number_of_assets)
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

    if len(forecast_volatilities) == 0:
        raise ValueError(
            "forecast_volatilities cannot be empty."
        )

    assets = list(
        forecast_volatilities.index
    )

    if list(correlation_matrix.index) != assets:
        raise ValueError(
            "Correlation matrix index must match assets."
        )

    if list(correlation_matrix.columns) != assets:
        raise ValueError(
            "Correlation matrix columns must match assets."
        )

    if simulations <= 0:
        raise ValueError(
            "simulations must be positive."
        )

    if horizon <= 0:
        raise ValueError(
            "horizon must be positive."
        )

    volatility_vector = (
        forecast_volatilities.to_numpy(
            dtype=float
        )
    )

    correlation = (
        correlation_matrix.to_numpy(
            dtype=float
        )
    )

    if not np.all(
        np.isfinite(volatility_vector)
    ):
        raise ValueError(
            "Volatilities must be finite."
        )

    if not np.all(
        np.isfinite(correlation)
    ):
        raise ValueError(
            "Correlation matrix must be finite."
        )

    if np.any(
        volatility_vector <= 0
    ):
        raise ValueError(
            "Volatilities must be positive."
        )

    # Convert annualized volatility and correlation
    # into daily covariance.
    covariance = (
        np.outer(
            volatility_vector,
            volatility_vector,
        )
        * correlation
        / 252
    )

    # Protect against tiny floating-point asymmetry.
    covariance = (
        covariance + covariance.T
    ) / 2

    rng = np.random.default_rng(seed)

    # Simulate correlated asset returns.
    asset_returns = rng.multivariate_normal(
        mean=np.zeros(len(assets)),
        cov=covariance,
        size=(simulations, horizon),
    )

    return asset_returns


def simulate_portfolio_returns(
    forecast_volatilities,
    correlation_matrix,
    weights,
    simulations=10000,
    horizon=21,
    seed=42,
):
    """
    Simulate correlated daily portfolio returns.

    Returns
    -------
    np.ndarray
        Shape: (simulations, horizon)
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

    if not isinstance(weights, dict):
        raise ValueError(
            "weights must be a dictionary."
        )

    if not weights:
        raise ValueError(
            "weights cannot be empty."
        )

    if simulations <= 0:
        raise ValueError(
            "simulations must be positive."
        )

    if horizon <= 0:
        raise ValueError(
            "horizon must be positive."
        )

    assets = list(weights.keys())

    if set(forecast_volatilities.index) != set(
        assets
    ):
        raise ValueError(
            "Forecast volatility assets must match weights."
        )

    if (
        set(correlation_matrix.index) != set(assets)
        or
        set(correlation_matrix.columns) != set(assets)
    ):
        raise ValueError(
            "Correlation matrix assets must match weights."
        )

    # Keep all inputs in exactly the same asset order.
    forecast_volatilities = (
        forecast_volatilities.loc[assets]
    )

    correlation_matrix = (
        correlation_matrix.loc[
            assets,
            assets,
        ]
    )

    weight_vector = np.array(
        [
            weights[asset]
            for asset in assets
        ],
        dtype=float,
    )

    if not np.all(
        np.isfinite(weight_vector)
    ):
        raise ValueError(
            "Weights contain invalid values."
        )

    # Generate asset-level paths.
    asset_returns = simulate_asset_returns(
        forecast_volatilities=forecast_volatilities,
        correlation_matrix=correlation_matrix,
        simulations=simulations,
        horizon=horizon,
        seed=seed,
    )

    # Convert asset returns into portfolio returns.
    portfolio_returns = (
        asset_returns @ weight_vector
    )

    return portfolio_returns


def calculate_cumulative_returns(
    simulated_returns,
):
    """
    Calculate cumulative portfolio return for
    each simulated path.

    Parameters
    ----------
    simulated_returns : np.ndarray
        Daily simulated returns.
        Shape: (simulations, horizon)

    Returns
    -------
    np.ndarray
        Final cumulative return for each simulation.
    """

    if not isinstance(
        simulated_returns,
        np.ndarray,
    ):
        raise ValueError(
            "simulated_returns must be a numpy array."
        )

    if simulated_returns.ndim != 2:
        raise ValueError(
            "simulated_returns must be 2-dimensional."
        )

    if simulated_returns.shape[1] == 0:
        raise ValueError(
            "Simulation horizon cannot be empty."
        )

    if not np.all(
        np.isfinite(simulated_returns)
    ):
        raise ValueError(
            "simulated_returns contains invalid values."
        )

    cumulative_returns = (
        np.prod(
            1 + simulated_returns,
            axis=1,
        )
        - 1
    )

    return cumulative_returns


def calculate_monte_carlo_var(
    cumulative_returns,
    confidence_level=0.95,
):
    """
    Calculate Monte Carlo VaR from simulated
    cumulative portfolio returns.

    Returns a positive loss percentage.
    """

    if not isinstance(
        cumulative_returns,
        np.ndarray,
    ):
        raise ValueError(
            "cumulative_returns must be a numpy array."
        )

    if cumulative_returns.ndim != 1:
        raise ValueError(
            "cumulative_returns must be 1-dimensional."
        )

    if len(cumulative_returns) == 0:
        raise ValueError(
            "cumulative_returns cannot be empty."
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if not np.all(
        np.isfinite(cumulative_returns)
    ):
        raise ValueError(
            "cumulative_returns contains invalid values."
        )

    percentile = (
        1 - confidence_level
    ) * 100

    threshold = np.percentile(
        cumulative_returns,
        percentile,
    )

    return -threshold


def calculate_monte_carlo_cvar(
    cumulative_returns,
    confidence_level=0.95,
):
    """
    Calculate Monte Carlo CVaR / Expected Shortfall
    from simulated cumulative portfolio returns.

    Returns a positive expected loss in the
    worst (1 - confidence_level) portion of simulations.
    """

    if not isinstance(
        cumulative_returns,
        np.ndarray,
    ):
        raise ValueError(
            "cumulative_returns must be a numpy array."
        )

    if cumulative_returns.ndim != 1:
        raise ValueError(
            "cumulative_returns must be 1-dimensional."
        )

    if len(cumulative_returns) == 0:
        raise ValueError(
            "cumulative_returns cannot be empty."
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if not np.all(
        np.isfinite(cumulative_returns)
    ):
        raise ValueError(
            "cumulative_returns contains invalid values."
        )

    percentile = (
        1 - confidence_level
    ) * 100

    threshold = np.percentile(
        cumulative_returns,
        percentile,
    )

    tail_returns = cumulative_returns[
        cumulative_returns <= threshold
    ]

    if len(tail_returns) == 0:
        raise ValueError(
            "No observations found in the VaR tail."
        )

    return -tail_returns.mean()