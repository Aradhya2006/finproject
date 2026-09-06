from src.data.loader import load_raw_nse_files
from src.data.cleaner import clean_loaded_nse_data
from src.data.validator import validate_nse_data
from src.data.saver import save_processed_data

print("Loading raw TCS data...")
df = load_raw_nse_files("TCS")

print("Raw shape:", df.shape)

print()
print("Cleaning TCS data...")

df = clean_loaded_nse_data(df)

print("Cleaned shape:", df.shape)

print()
print("Validating TCS data...")

validate_nse_data(df)

print()
print("PIPELINE VALIDATION PASSED!")


print()
print("Data types:")
print(df.dtypes)

print()
print("First 5 rows:")
print(df.head())

print()
print("Last 5 rows:")
print(df.tail())


file_path = save_processed_data(
    df,
    "TCS",
)

print()
print("Processed data saved to:")
print(file_path)