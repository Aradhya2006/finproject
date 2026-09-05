from src.data.loader import load_raw_nse_files


df = load_raw_nse_files("TCS")

print("TCS combined data")
print("=" * 40)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print()
print("Columns:")
for column in df.columns:
    print(repr(column))

print()
print("Duplicate rows:", df.duplicated().sum())

print()
print("First raw date:")
print(df["Date  "].iloc[0])

print()
print("Last raw date:")
print(df["Date  "].iloc[-1])