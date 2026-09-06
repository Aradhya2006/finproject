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