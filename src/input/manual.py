from src.data.current_prices import get_latest_prices
from src.finance.portfolio import (
    calculate_holding_values,
    calculate_portfolio_value,
    calculate_portfolio_weights,
)


def validate_holdings(holdings):
    """
    Validate and normalize user-provided holdings.

    Parameters
    ----------
    holdings : dict
        Symbol -> quantity.

    Returns
    -------
    dict
        Normalized holdings.
    """

    if not isinstance(holdings, dict):
        raise ValueError(
            "Holdings must be a dictionary."
        )

    if not holdings:
        raise ValueError(
            "Holdings cannot be empty."
        )

    validated_holdings = {}

    for symbol, quantity in holdings.items():

        if not isinstance(symbol, str):
            raise ValueError(
                "Stock symbols must be strings."
            )

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Stock symbol cannot be empty."
            )

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid quantity for {symbol}."
            )

        if quantity <= 0:
            raise ValueError(
                f"Quantity for {symbol} must be positive."
            )

        validated_holdings[symbol] = quantity

    return validated_holdings


def create_manual_portfolio(holdings):
    """
    Create a validated manual portfolio representation.
    """

    validated_holdings = validate_holdings(
        holdings
    )

    return {
        "holdings": validated_holdings,
        "assets": list(
            validated_holdings.keys()
        ),
    }


def calculate_portfolio_from_holdings(
    holdings,
    prices,
):
    """
    Calculate portfolio valuation from holdings
    and supplied prices.
    """

    validated_holdings = validate_holdings(
        holdings
    )

    if not isinstance(prices, dict):
        raise ValueError(
            "Prices must be a dictionary."
        )

    clean_prices = {}

    for symbol in validated_holdings:

        if symbol not in prices:
            raise ValueError(
                f"Missing price for {symbol}."
            )

        try:
            price = float(prices[symbol])
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid price for {symbol}."
            )

        if price <= 0:
            raise ValueError(
                f"Price for {symbol} must be positive."
            )

        clean_prices[symbol] = price

    holding_values = calculate_holding_values(
        validated_holdings,
        clean_prices,
    )

    portfolio_value = calculate_portfolio_value(
        holding_values
    )

    weights = calculate_portfolio_weights(
        holding_values
    )

    return {
        "holdings": validated_holdings,
        "prices": clean_prices,
        "holding_values": holding_values,
        "portfolio_value": portfolio_value,
        "weights": weights,
        "assets": list(
            validated_holdings.keys()
        ),
    }


def create_current_manual_portfolio(holdings):
    """
    Validate manual holdings, obtain the latest
    available NSE prices, and calculate the
    current portfolio valuation.
    """

    validated_holdings = validate_holdings(
        holdings
    )

    assets = list(
        validated_holdings.keys()
    )

    prices = get_latest_prices(
        assets
    )

    return calculate_portfolio_from_holdings(
        validated_holdings,
        prices,
    )