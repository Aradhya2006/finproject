from src.data.loader import load_raw_nse_files
from src.data.cleaner import clean_loaded_nse_data
from src.data.validator import validate_nse_data
from src.finance.returns import calculate_daily_returns
from src.finance.volatility import (
    calculate_daily_volatility,
    calculate_annualized_volatility,
)


def test_volatility():
    df = load_raw_nse_files("TCS")
    df = clean_loaded_nse_data(df)

    validate_nse_data(df)

    df = calculate_daily_returns(df)

    daily_volatility = calculate_daily_volatility(df)
    annualized_volatility = calculate_annualized_volatility(df)

    assert daily_volatility > 0
    assert annualized_volatility > daily_volatility

    print(f"Daily volatility: {daily_volatility:.6f}")
    print(f"Annualized volatility: {annualized_volatility:.6f}")
    print(f"Annualized volatility in Percent: {annualized_volatility * 100:.2f}%")


if __name__ == "__main__":
    test_volatility()
    print("Volatility test passed!")