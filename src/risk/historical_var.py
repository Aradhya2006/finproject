import numpy as np

def calculate_historical_var(portfolio_returns , confidence_level = 0.95):
    returns = portfolio_returns.dropna()

    tail_probability =  1- confidence_level

    percentile_return = np.percentile(returns,tail_probability * 100,)
    var = -percentile_return
    return var


def calculate_var_value(var_percentage,portfolio_value):
    if portfolio_value <= 0:
        raise ValueError(
            "Portfolio value must be greater than zero."
        )

    return var_percentage * portfolio_value