import numpy as np


def calculate_monte_carlo_var(portfolio_returns,confidence_level=0.95,simulations=10000,random_seed=42):
    returns = portfolio_returns.dropna()

    mean_return = returns.mean()
    volatility = returns.std(ddof=1)

    rng = np.random.default_rng(random_seed)

    random_returns = rng.normal(
        loc=mean_return,
        scale=volatility,
        size=simulations,
    )

    tail_probability = 1 - confidence_level

    percentile_return = np.percentile(
        random_returns,
        tail_probability * 100,
    )

    var = -percentile_return

    return var