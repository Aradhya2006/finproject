def calculate_holding_values(holdings,prices):
    holding_values = {}

    for symbol , quantity in holdings.items():
        if symbol not in prices:
            raise ValueError(f"Price not available for {symbol}.")

        holding_values[symbol] = (quantity * prices[symbol])

    return holding_values



def calculate_portfolio_value(holding_values):
    return sum(holding_values.values())

def calculate_portfolio_weights(holding_values):
    total_value = calculate_portfolio_value(holding_values)

    if total_value <= 0:
        raise ValueError("Portfolio Value Must be greater Than zero.")

    weights = {}

    for symbol, value in holding_values.items():
        weights[symbol] = value / total_value

    return weights

def calculate_portfolio_returns(asset_returns, weights):
    portfolio_returns = asset_returns.copy()

    for symbol, weight in weights.items():
        if symbol not in portfolio_returns.columns:
            raise ValueError(
                f"Returns not available for {symbol}."
            )

        portfolio_returns[symbol] = (
            portfolio_returns[symbol] * weight
        )

    portfolio_returns["PORTFOLIO RETURN"] = (
        portfolio_returns[list(weights.keys())].sum(axis=1)
    )

    return portfolio_returns