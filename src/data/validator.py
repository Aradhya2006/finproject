import pandas as pd


REQUIRED_COLUMNS = [
    "DATE",
    "SERIES",
    "OPEN",
    "HIGH",
    "LOW",
    "PREV. CLOSE",
    "LTP",
    "CLOSE",
    "VWAP",
    "VOLUME",
    "VALUE",
    "NO. OF  TRADES",
]


def validate_columns(df):
# check for required colunns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


def validate_dates(df):

    if df["DATE"].isna().any():
        raise ValueError("DATE contains missing values.")

    if df["DATE"].duplicated().any():
        raise ValueError("DATE contains duplicate dates.")

    if not df["DATE"].is_monotonic_increasing:
        raise ValueError("DATE is not sorted in ascending order.")

    return True


def validate_prices(df):

    price_columns = [
        "OPEN",
        "HIGH",
        "LOW",
        "PREV. CLOSE",
        "LTP",
        "CLOSE",
        "VWAP",
    ]

    for column in price_columns:
        if df[column].isna().any():
            raise ValueError(
                f"{column} contains missing values."
            )

        if (df[column] <= 0).any():
            raise ValueError(
                f"{column} contains non-positive values."
            )

    if (df["HIGH"] < df["LOW"]).any():
        raise ValueError("HIGH is lower than LOW.")

    return True


def validate_volume(df):

    if df["VOLUME"].isna().any():
        raise ValueError("VOLUME contains missing values.")

    if (df["VOLUME"] < 0).any():
        raise ValueError("VOLUME contains negative values.")

    return True


def validate_nse_data(df):
# FINAL CHECK
    validate_columns(df)
    validate_dates(df)
    validate_prices(df)
    validate_volume(df)

    return True