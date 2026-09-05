from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw/nse")

def normalize_nse_columns(df):
    """
    Normalize NSE API column names into a consistent schema.
    """

    column_mapping = {
        "Symbol  ": "SYMBOL",
        "Series  ": "SERIES",
        "Date  ": "DATE",
        "Prev Close  ": "PREV. CLOSE",
        "Open Price  ": "OPEN",
        "High Price  ": "HIGH",
        "Low Price  ": "LOW",
        "Last Price  ": "LTP",
        "Close Price  ": "CLOSE",
        "Average Price ": "VWAP",
        "Total Traded Quantity  ": "VOLUME",
        "Turnover ₹  ": "VALUE",
        "No. of Trades  ": "NO. OF TRADES",
        "Deliverable Qty  ": "DELIVERABLE QTY",
        "% Dly Qt to Traded Qty  ": "DELIVERABLE %",
    }

    df = df.rename(columns=column_mapping)

    return df

def load_raw_nse_files(symbol):
    """
    Load all six-month NSE CSV files for a symbol.
    """

    symbol = symbol.strip().upper()

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

    combined = pd.concat(
        dataframes,
        ignore_index=True,
    )

    combined = combined.sort_values(
        "DATE",
        key=lambda column: pd.to_datetime(
            column,
            format="%d-%b-%Y",
        )
    ).reset_index(drop=True)

    return combined