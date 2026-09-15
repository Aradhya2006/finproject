from src.input.portfolio_input import PortfolioInput


def validate_portfolio_values(values):
    """
    Validate current portfolio values.

    Parameters
    ----------
    values : dict
        Symbol -> current portfolio value

    Returns
    -------
    dict
        Validated portfolio values
    """

    if not isinstance(values, dict):
        raise ValueError(
            "Portfolio values must be provided as a dictionary."
        )

    if not values:
        raise ValueError(
            "Portfolio values cannot be empty."
        )

    validated_values = {}

    for symbol, value in values.items():

        if not isinstance(symbol, str):
            raise ValueError(
                "Symbol must be a string."
            )

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Symbol cannot be empty."
            )

        if isinstance(value, bool):
            raise ValueError(
                f"Invalid portfolio value for {symbol}."
            )

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid portfolio value for {symbol}."
            )

        if value <= 0:
            raise ValueError(
                f"Portfolio value for {symbol} must be positive."
            )

        validated_values[symbol] = value

    return validated_values


def create_value_portfolio(values):
    """
    Create a portfolio from current asset values.

    Parameters
    ----------
    values : dict
        Symbol -> current portfolio value

    Returns
    -------
    PortfolioInput
    """

    values = validate_portfolio_values(values)

    portfolio_value = sum(values.values())

    weights = {
        symbol: value / portfolio_value
        for symbol, value in values.items()
    }

    assets = list(values.keys())

    return PortfolioInput(
        holdings=values.copy(),
        prices={},
        holding_values=values.copy(),
        portfolio_value=portfolio_value,
        weights=weights,
        assets=assets,
        source="value",
    )