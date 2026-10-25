from src.data.loader import load_raw_nse_files


df = load_raw_nse_files("TCS")

print("TCS raw data loaded successfully!")
print()
print("Shape:", df.shape)
print()
print("Columns:")
print(df.columns.tolist())
print()
print("First 5 rows:")
print(df.head())
print()
print("Last 5 rows:")
print(df.tail())