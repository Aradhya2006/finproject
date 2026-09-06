import pandas as pd

from src.data.loader import load_raw_nse_files
from src.data.cleaner import clean_loaded_nse_data
from src.data.validator import validate_nse_data


def load_clean_asset_data(symbol):
    df = load_raw_nse_files(symbol)
    df = clean_loaded_nse_data(df)
    validate_nse_data(df)

    return df


def create_price_dataset(symbols):
    price_data = []

    for symbol in symbols:
        df = load_clean_asset_data(symbol)

        prices = df[["DATE", "CLOSE"]].copy()

        prices = prices.rename(
            columns={"CLOSE": symbol}
        )

        price_data.append(prices)

    combined = price_data[0]

    for prices in price_data[1:]:
        combined = combined.merge(
            prices,
            on="DATE",
            how="inner",
        )

    combined = combined.sort_values(
        "DATE"
    ).reset_index(drop=True)

    return combined


def calculate_asset_returns(price_data):
    returns = price_data.copy()

    symbols = [
        column
        for column in returns.columns
        if column != "DATE"
    ]

    for symbol in symbols:
        returns[symbol] = (
            returns[symbol]
            / returns[symbol].shift(1)
            - 1
        )

    return returns