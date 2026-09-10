from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import calculate_portfolio_returns

from src.forecasting.dl_preprocessing import prepare_lstm_data

from src.forecasting.baseline_evaluation import (
    evaluate_baseline_models,
)


symbols = [
    "TCS",
    "INFY",
    "HCLTECH",
    "WIPRO",
    "RELIANCE",
]

weights = {
    "TCS": 0.25,
    "INFY": 0.25,
    "HCLTECH": 0.20,
    "WIPRO": 0.15,
    "RELIANCE": 0.15,
}


# ---------------------------------------------------------
# Load Portfolio A
# ---------------------------------------------------------

prices = create_price_dataset(symbols)

asset_returns = (
    calculate_asset_returns(prices)
    .set_index("DATE")
)

portfolio_returns = calculate_portfolio_returns(
    asset_returns,
    weights,
)["PORTFOLIO RETURN"]


# ---------------------------------------------------------
# Get the exact LSTM test dates
# ---------------------------------------------------------

data = prepare_lstm_data(
    portfolio_returns,
    lookback=60,
    horizon=21,
    test_months=6,
)

test_dates = data["dates_test"]


# ---------------------------------------------------------
# Evaluate Rolling + EWMA
# ---------------------------------------------------------

comparison, results = evaluate_baseline_models(
    portfolio_returns,
    test_dates,
    rolling_window=21,
    ewma_lambda=0.94,
    horizon=21,
)


print("\nOOS BASELINE RESULTS")
print("====================")

for model, metrics in results.items():

    print(f"\n{model}")

    for key, value in metrics.items():
        print(f"{key}: {value}")


print("\nComparison rows:", len(comparison))
print("Comparison start:", comparison.index.min())
print("Comparison end:", comparison.index.max())
