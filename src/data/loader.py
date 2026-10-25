import re
from pathlib import Path

import pandas as pd


# Anchored to the project root so the data path does not depend on the
# directory the server was started from.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "nse"

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9&-]{1,20}$")

# Lower-cased, whitespace-collapsed header -> standard column name.
# Covers NSE equity exports, NSE index exports and generic OHLCV files.
COLUMN_ALIASES = {
    "symbol": "SYMBOL",
    "series": "SERIES",
    "date": "DATE",
    "index date": "DATE",
    "prev close": "PREV. CLOSE",
    "prev. close": "PREV. CLOSE",
    "open price": "OPEN",
    "open": "OPEN",
    "open index value": "OPEN",
    "high price": "HIGH",
    "high": "HIGH",
    "high index value": "HIGH",
    "low price": "LOW",
    "low": "LOW",
    "low index value": "LOW",
    "last price": "LTP",
    "ltp": "LTP",
    "close price": "CLOSE",
    "close": "CLOSE",
    "closing index value": "CLOSE",
    "average price": "VWAP",
    "vwap": "VWAP",
    "total traded quantity": "VOLUME",
    "volume": "VOLUME",
    "turnover ₹": "VALUE",
    "turnover": "VALUE",
    "no. of trades": "NO. OF TRADES",
    "deliverable qty": "DELIVERABLE QTY",
    "% dly qt to traded qty": "DELIVERABLE %",
}


def validate_symbol_name(symbol):
    """
    Return the normalized ticker, or raise if it is not a safe ticker.

    The ticker is used as a directory name, so only plain letters,
    digits, '&' and '-' are accepted.
    """

    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string.")

    symbol = symbol.strip().upper()

    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Use 1-20 letters, digits, '&' or '-'."
        )

    return symbol


def normalize_nse_columns(df):
    """
    Normalize NSE API column names into a consistent schema.

    Matching ignores case and extra whitespace, so headers such as
    "Close Price  " and "Close" both map to CLOSE.
    """

    rename = {}

    for column in df.columns:
        key = " ".join(str(column).split()).lower()
        if key in COLUMN_ALIASES:
            rename[column] = COLUMN_ALIASES[key]

    return df.rename(columns=rename)


def load_raw_nse_files(symbol):
    """
    Load all six-month NSE CSV files for a symbol.
    """

    symbol = validate_symbol_name(symbol)

    symbol_dir = RAW_DATA_DIR / symbol

    if not symbol_dir.exists():
        raise FileNotFoundError(
            f"No raw data directory found for {symbol}."
        )

    files = sorted(
        symbol_dir.glob(f"{symbol}_EQ_*.csv")
    )

    if not files:
        raise FileNotFoundError(
            f"No six-month CSV files found for {symbol}."
        )

    dataframes = []

    for file_path in files:

        df = pd.read_csv(file_path)

        df = normalize_nse_columns(df)

        dataframes.append(df)

    combined = pd.concat(dataframes, ignore_index=True)

    combined["DATE"] = pd.to_datetime(
        combined["DATE"],
        format="mixed",
        dayfirst=True,
    )

    # Files can overlap (e.g. a month inside two downloads, or an uploaded
    # file covering dates already on disk). Keep one row per date; files are
    # read in name order, so later uploads (named *_EQ_UPLOAD_*) win.
    combined = (
        combined
        .sort_values("DATE", kind="stable")
        .drop_duplicates(subset="DATE", keep="last")
        .reset_index(drop=True)
    )

    return combined