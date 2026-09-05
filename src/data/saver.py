from pathlib import Path

import pandas as pd


PROCESSED_DATA_DIR = Path("data/processed")


def save_processed_data(df, symbol):


    symbol = symbol.strip().upper()

    symbol_dir = PROCESSED_DATA_DIR / symbol
    symbol_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        symbol_dir / f"{symbol}_cleaned.csv"
    )

    df.to_csv(
        destination,
        index=False,
    )

    return destination