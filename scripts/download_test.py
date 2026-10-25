import sys
from pathlib import Path

# Make the project root importable when run as python scripts/<name>.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.downloader import download_full_history

symbols = [
    "INFY",
    "HCLTECH",
    "WIPRO",
    "RELIANCE",
]

for symbol in symbols:
    download_full_history(
        symbol,
        "01-01-2015",
        "05-09-2026",
    )