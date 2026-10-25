import pandas as pd

file_path = (
    "data/raw/nse/TCS/"
    "TCS_EQ_01-01-2015_31-01-2015.csv"
)

df = pd.read_csv(file_path)

print("Shape:", df.shape)
print()
print("Columns:")
print(df.columns.tolist())
print()
print(df.head())