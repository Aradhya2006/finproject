import pandas as pd


manual_file = (
    "data/raw/nse/"
    "Quote-Equity-TCS-EQ-01-01-2015-31-01-2015.csv"
)

api_file = (
    "data/raw/nse/TCS/"
    "TCS_EQ_01-01-2015_31-01-2015.csv"
)


manual = pd.read_csv(manual_file)
api = pd.read_csv(api_file)


# Remove whitespace from column names
manual.columns = manual.columns.str.strip()
api.columns = api.columns.str.strip()


# Parse dates
manual["Date"] = pd.to_datetime(
    manual["DATE"],
    format="%d-%b-%y"
)

api["Date"] = pd.to_datetime(
    api["Date"],
    format="%d-%b-%Y"
)


# Convert close prices to numeric
manual["Close"] = (
    manual["CLOSE"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .astype(float)
)

api["Close"] = (
    api["Close Price"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .astype(float)
)


# Sort both datasets
manual = manual.sort_values("Date")
api = api.sort_values("Date")


print("Manual CSV rows:", len(manual))
print("API CSV rows:", len(api))
print()


# Compare dates
dates_match = manual["Date"].tolist() == api["Date"].tolist()

print("Dates match:", dates_match)


# Compare close prices
close_match = (
    manual["Close"].round(2).tolist()
    == api["Close"].round(2).tolist()
)

print("Close prices match:", close_match)
print()


if dates_match and close_match:
    print("API VALIDATION PASSED!")
    print("NSE API data matches the original NSE CSV.")
else:
    print("API VALIDATION FAILED!")

    print()
    print("Comparison:")

    comparison = pd.merge(
        manual[["Date", "Close"]],
        api[["Date", "Close"]],
        on="Date",
        how="outer",
        suffixes=("_manual", "_api"),
    )

    print(comparison)