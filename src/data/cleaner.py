import pandas as pd

NUMERIC_COLUMNS = [
    "OPEN",
    "HIGH",
    "LOW",
    "PREV. CLOSE",
    "LTP",
    "CLOSE",
    "VWAP",
    "VOLUME",
    "VALUE",
    "NO. OF TRADES",
    "DELIVERABLE QTY",
    "DELIVERABLE %",
]

def load_raw_csv(file_path):
    return pd.read_csv(file_path)

def clean_dates(df):
    df = df.copy()
    df["DATE"] = pd.to_datetime(
    df["DATE"],
    format="mixed",
    dayfirst=True,
)
    return df

def clean_numeric_columns(df):
    df = df.copy()

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .replace("-", pd.NA)
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    return df


def sort_by_date(df):
    return df.sort_values("DATE").reset_index(drop=True)

def clean_nse_data(file_path):
    df = load_raw_csv(file_path)
    df = clean_dates(df)
    df = clean_numeric_columns(df)
    df = sort_by_date(df)
    return df


def clean_loaded_nse_data(df):
    """
    Clean an already-loaded and combined NSE dataset.
    """

    df = df.copy()

    df = clean_dates(df)

    df = clean_numeric_columns(df)

    df = sort_by_date(df)
    return df