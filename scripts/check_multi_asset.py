import sys
from pathlib import Path

# Make the project root importable when run as python scripts/<name>.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.data.loader import load_raw_nse_files


symbols = [
    "TCS",
    "INFY",
    "HCLTECH",
    "WIPRO",
    "RELIANCE",
]

for symbol in symbols:
    df = load_raw_nse_files(symbol)

    dates = pd.to_datetime(
        df["DATE"],
        format="%d-%b-%Y",
    )

    print(
        f"{symbol}: "
        f"shape={df.shape}, "
        f"start={dates.min().date()}, "
        f"end={dates.max().date()}"
    )