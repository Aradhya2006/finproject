from src.data.downloader import download_full_history


result = download_full_history(
    symbol="TCS",
    start_date="01-01-2015",
    end_date="05-09-2026",
    delay_seconds=1,
)

print()
print("Downloaded:", len(result["downloaded"]))
print("Skipped:", len(result["skipped"]))
print("Failed:", len(result["failed"]))