from src.data.downloader import download_nse_data


file_path = download_nse_data(
    symbol="TCS",
    start_date="01-01-2015",
    end_date="31-01-2015",
)

print("NSE download successful!")
print()
print("Saved to:")
print(file_path)