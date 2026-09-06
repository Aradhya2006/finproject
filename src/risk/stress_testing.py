def calculate_stress_loss(weights,shocks):
    missing_symbols = [symbol for symbol in weights if symbol not in shocks]

    if missing_symbols:
        raise ValueError(f"Shocks not provided for {missing_symbols}.")

    portfolio_return = sum(weights[symbol] * shocks[symbol] for symbol in weights)

    return portfolio_return


def calculate_stress_loss_value(portfolio_return,portfolio_value):
    if portfolio_value <= 0:
        raise ValueError("Portfolio value must be greater than zero.")

    return -portfolio_return * portfolio_value
