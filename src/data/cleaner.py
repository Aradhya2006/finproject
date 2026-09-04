import pandas as pd

NUMERIC_COLUMNS = [
    "OPEN",
    "HIGH",
    "LOW",
    "PREV. CLOSE",
    "LTP",
    "CLOSE",
    "VWAP",
    "52 WEEK HIGH",
    "52 WEEK LOW",
    "VOLUME",
    "VALUE",
    "NO. OF  TRADES",
]

def load_raw_csv(file_path):
    return pd.read_csv(file_path)

def clean_dates(df):
    df = df.copy()
    df["DATE"] = pd.to_datetime(
    df["DATE"],
    format="%d-%b-%y"
)   
    return df

def clean_numeric_columns(df):
    df = df.copy()

    for col in NUMERIC_COLUMNS:
        df[col] = (df[col].astype(str).str.replace(",","", regex = False).astype(float))


    return df


def sort_by_date(df):
    return df.sort_values("DATE").reset_index(drop=True)

def clean_nse_data(file_path):
    df = load_raw_csv(file_path)
    df = clean_dates(df)
    df = clean_numeric_columns(df)
    df = sort_by_date(df)


    return df