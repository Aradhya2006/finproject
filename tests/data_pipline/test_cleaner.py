from src.data.cleaner import clean_nse_data
from src.data.validator import validate_nse_data

file_path = "data/raw/nse/Quote-Equity-TCS-EQ-01-01-2015-31-01-2015.csv"

df = clean_nse_data(file_path)

validate_nse_data(df)


print("Data is valid")
print(df.head())
print()
print(df.dtypes)
print()
print("Shape:", df.shape)