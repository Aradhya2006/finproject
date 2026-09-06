import numpy as np


def calculate_parametric_var(
    portfolio_returns,
    confidence_level=0.95,
):
    returns = portfolio_returns.dropna()

    mean_return = returns.mean()
    volatility = returns.std(ddof=1)

    tail_probability = 1 - confidence_level

    z_score = {
        0.90: -1.2816,
        0.95: -1.6449,
        0.99: -2.3263,
    }

    if confidence_level not in z_score:
        raise ValueError(
            "Supported confidence levels: 0.90, 0.95, 0.99"
        )

    z = z_score[confidence_level]

    percentile_return = (
        mean_return + z * volatility
    )

    var = -percentile_return

    return var