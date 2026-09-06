from src.data.loader import load_raw_nse_files
from src.data.cleaner import clean_loaded_nse_data
from src.data.validator import validate_nse_data
from src.finance.returns import calculate_daily_returns


def test_daily_returns():
    df = load_raw_nse_files("TCS")
    df = clean_loaded_nse_data(df)

    validate_nse_data(df)

    df = calculate_daily_returns(df)

    assert "DAILY RETURN" in df.columns
    assert df["DAILY RETURN"].iloc[0] != df["DAILY RETURN"].iloc[0]
    assert df["DAILY RETURN"].iloc[1] == (
        df["CLOSE"].iloc[1] / df["CLOSE"].iloc[0] - 1
    )

    print(df[["DATE", "CLOSE", "DAILY RETURN"]].head())


if __name__ == "__main__":
    test_daily_returns()
    print("Daily returns test passed!")