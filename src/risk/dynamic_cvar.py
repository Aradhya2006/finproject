import numpy as np


def calculate_dynamic_parametric_cvar(
    portfolio_volatility,
    confidence_level=0.95,
    portfolio_value=1.0,
):
    """
    Calculate one-day parametric CVaR using
    dynamically forecasted annualized volatility.

    Assumes normally distributed daily returns
    with zero expected return.
    """

    if portfolio_volatility <= 0:
        raise ValueError(
            "portfolio_volatility must be positive."
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if portfolio_value <= 0:
        raise ValueError(
            "portfolio_value must be positive."
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

    daily_volatility = (
        portfolio_volatility / np.sqrt(252)
    )

    z = z_scores[confidence_level]

    # Standard normal PDF
    pdf = (
        np.exp(-0.5 * z**2)
        / np.sqrt(2 * np.pi)
    )

    # Expected loss beyond VaR under normality
    cvar_return = (
        daily_volatility
        * pdf
        / (1 - confidence_level)
    )

    return cvar_return * portfolio_value