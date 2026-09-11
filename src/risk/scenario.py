import numpy as np


def apply_portfolio_shock(
    weights,
    shocks,
):
    """
    Apply asset-level percentage shocks to a portfolio.
    """

    if not isinstance(weights, dict):
        raise ValueError(
            "weights must be a dictionary."
        )

    if not weights:
        raise ValueError(
            "weights cannot be empty."
        )

    if not isinstance(shocks, dict):
        raise ValueError(
            "shocks must be a dictionary."
        )

    missing_assets = [
        asset
        for asset in shocks
        if asset not in weights
    ]

    if missing_assets:
        raise ValueError(
            f"Shocks contain unknown assets: "
            f"{missing_assets}"
        )

    portfolio_shock = 0.0

    for asset, weight in weights.items():

        shock = shocks.get(
            asset,
            0.0,
        )

        portfolio_shock += (
            weight * shock
        )

    return portfolio_shock


def apply_sector_shock(
    weights,
    asset_sectors,
    sector,
    shock,
):
    """
    Apply the same percentage shock to all assets
    belonging to a specified sector.
    """

    if not isinstance(
        asset_sectors,
        dict,
    ):
        raise ValueError(
            "asset_sectors must be a dictionary."
        )

    shocks = {}

    for asset in weights:

        if asset_sectors.get(asset) == sector:
            shocks[asset] = shock
        else:
            shocks[asset] = 0.0

    return apply_portfolio_shock(
        weights,
        shocks,
    )


def apply_broad_market_shock(
    weights,
    shock,
    excluded_assets=None,
):
    """
    Apply a broad market shock to portfolio assets.
    """

    if excluded_assets is None:
        excluded_assets = set()
    else:
        excluded_assets = set(
            excluded_assets
        )

    shocks = {}

    for asset in weights:

        if asset in excluded_assets:
            shocks[asset] = 0.0
        else:
            shocks[asset] = shock

    return apply_portfolio_shock(
        weights,
        shocks,
    )


def apply_single_asset_shock(
    weights,
    asset,
    shock,
):
    """
    Apply a shock to one asset while leaving
    all other assets unchanged.
    """

    if asset not in weights:
        raise ValueError(
            f"Unknown portfolio asset: {asset}"
        )

    shocks = {
        portfolio_asset: (
            shock
            if portfolio_asset == asset
            else 0.0
        )
        for portfolio_asset in weights
    }

    return apply_portfolio_shock(
        weights,
        shocks,
    )


def apply_shock_to_simulations(
    asset_returns,
    shocks,
    assets,
):
    """
    Apply an immediate deterministic shock to the
    first day of every simulated asset path.

    Parameters
    ----------
    asset_returns : np.ndarray
        Simulated asset returns.

        Shape:
        (simulations, horizon, assets)

    shocks : dict
        Asset-level percentage shocks.

        Example:
        {
            "TCS": -0.20,
            "INFY": -0.20
        }

    assets : list
        Asset ordering used by the simulation.

    Returns
    -------
    np.ndarray
        Asset returns after applying the scenario shock.
    """

    if not isinstance(
        asset_returns,
        np.ndarray,
    ):
        raise ValueError(
            "asset_returns must be a numpy array."
        )

    if asset_returns.ndim != 3:
        raise ValueError(
            "asset_returns must be 3-dimensional."
        )

    if not np.all(
        np.isfinite(asset_returns)
    ):
        raise ValueError(
            "asset_returns contains invalid values."
        )

    if len(assets) != asset_returns.shape[2]:
        raise ValueError(
            "Number of assets must match simulation data."
        )

    if not isinstance(
        shocks,
        dict,
    ):
        raise ValueError(
            "shocks must be a dictionary."
        )

    unknown_assets = [
        asset
        for asset in shocks
        if asset not in assets
    ]

    if unknown_assets:
        raise ValueError(
            f"Shocks contain unknown assets: "
            f"{unknown_assets}"
        )

    shocked_returns = asset_returns.copy()

    asset_positions = {
        asset: i
        for i, asset in enumerate(assets)
    }

    for asset, shock in shocks.items():

        if not np.isfinite(shock):
            raise ValueError(
                "Shock values must be finite."
            )

        position = asset_positions[asset]

        # Replace the first simulated day with
        # the deterministic scenario shock.
        shocked_returns[:, 0, position] = shock

    return shocked_returns


def calculate_scenario_portfolio_returns(
    asset_returns,
    weights,
):
    """
    Convert scenario-adjusted asset returns into
    portfolio returns.

    Parameters
    ----------
    asset_returns : np.ndarray
        Shape:
        (simulations, horizon, assets)

    weights : dict
        Portfolio weights.

    Returns
    -------
    np.ndarray
        Shape:
        (simulations, horizon)
    """

    if not isinstance(
        asset_returns,
        np.ndarray,
    ):
        raise ValueError(
            "asset_returns must be a numpy array."
        )

    if asset_returns.ndim != 3:
        raise ValueError(
            "asset_returns must be 3-dimensional."
        )

    assets = list(weights.keys())

    if len(assets) != asset_returns.shape[2]:
        raise ValueError(
            "Number of weights must match number of assets."
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

    portfolio_returns = (
        asset_returns @ weight_vector
    )

    return portfolio_returns


def calculate_scenario_cumulative_returns(
    portfolio_returns,
):
    """
    Calculate the final cumulative return of
    each scenario simulation.
    """

    if not isinstance(
        portfolio_returns,
        np.ndarray,
    ):
        raise ValueError(
            "portfolio_returns must be a numpy array."
        )

    if portfolio_returns.ndim != 2:
        raise ValueError(
            "portfolio_returns must be 2-dimensional."
        )

    if not np.all(
        np.isfinite(portfolio_returns)
    ):
        raise ValueError(
            "portfolio_returns contains invalid values."
        )

    return (
        np.prod(
            1 + portfolio_returns,
            axis=1,
        )
        - 1
    )


def calculate_scenario_var(
    cumulative_returns,
    confidence_level=0.95,
):
    """
    Calculate VaR from scenario simulation outcomes.
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

    percentile = (
        1 - confidence_level
    ) * 100

    threshold = np.percentile(
        cumulative_returns,
        percentile,
    )

    return -threshold


def calculate_scenario_cvar(
    cumulative_returns,
    confidence_level=0.95,
):
    """
    Calculate CVaR / Expected Shortfall from
    scenario simulation outcomes.
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

    percentile = (
        1 - confidence_level
    ) * 100

    threshold = np.percentile(
        cumulative_returns,
        percentile,
    )

    tail_returns = cumulative_returns[
        cumulative_returns < threshold
    ]

    if len(tail_returns) == 0:
        raise ValueError(
            "No observations found in the VaR tail."
        )

    return -tail_returns.mean()