from src.data.cleaner import (
    clean_dates,
    clean_numeric_columns,
)
from src.data.loader import load_raw_nse_files


def get_latest_prices(symbols):
    """
    Get the latest available NSE closing price
    for each requested asset.

    Parameters
    ----------
    symbols : list
        NSE symbols.

    Returns
    -------
    dict
        Symbol -> latest available closing price.
    """

    if not isinstance(symbols, list):
        raise ValueError(
            "symbols must be a list."
        )

    if not symbols:
        raise ValueError(
            "symbols cannot be empty."
        )

    normalized_symbols = []

    for symbol in symbols:

        if not isinstance(symbol, str):
            raise ValueError(
                "Symbols must be strings."
            )

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Symbol cannot be empty."
            )

        normalized_symbols.append(symbol)

    prices = {}

    for symbol in normalized_symbols:

        df = load_raw_nse_files(symbol)

        if df.empty:
            raise ValueError(
                f"No data found for {symbol}."
            )

        if "DATE" not in df.columns:
            raise ValueError(
                f"DATE column missing for {symbol}."
            )

        if "CLOSE" not in df.columns:
            raise ValueError(
                f"CLOSE column missing for {symbol}."
            )

        df = df.copy()

        df = clean_dates(df)
        df = clean_numeric_columns(df)

        df = (
            df.dropna(
                subset=["DATE", "CLOSE"]
            )
            .sort_values("DATE")
        )

        if df.empty:
            raise ValueError(
                f"No valid price data for {symbol}."
            )

        latest_price = float(
            df.iloc[-1]["CLOSE"]
        )

        if latest_price <= 0:
            raise ValueError(
                f"Invalid latest price for {symbol}."
            )

        prices[symbol] = latest_price

    return prices