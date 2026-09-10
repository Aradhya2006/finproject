from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import calculate_portfolio_returns

from src.forecasting.dl_preprocessing import (
    prepare_lstm_data,
)

from src.forecasting.evaluation_dataset import (
    create_oos_evaluation_dataset,
)

from src.forecasting.evaluation import (
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
)

from src.forecasting.garch_oos import (
    generate_garch_oos_forecasts,
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
# Get exact shared OOS dates
# ---------------------------------------------------------

data = prepare_lstm_data(
    portfolio_returns,
    lookback=60,
    horizon=21,
    test_months=6,
)

test_dates = data["dates_test"]


# ---------------------------------------------------------
# Shared realized-volatility target
# ---------------------------------------------------------

oos = create_oos_evaluation_dataset(
    portfolio_returns,
    test_dates,
    horizon=21,
)


# ---------------------------------------------------------
# GARCH OOS forecasts
# ---------------------------------------------------------

garch_forecast = generate_garch_oos_forecasts(
    portfolio_returns,
    test_dates,
    refit_frequency=21,
)


# ---------------------------------------------------------
# Align forecasts and target
# ---------------------------------------------------------

comparison = oos.copy()

comparison["GARCH"] = garch_forecast

comparison = comparison.dropna()


# ---------------------------------------------------------
# Evaluate
# ---------------------------------------------------------

mae = calculate_mae(
    comparison["REALIZED"],
    comparison["GARCH"],
)

rmse = calculate_rmse(
    comparison["REALIZED"],
    comparison["GARCH"],
)

correlation = calculate_forecast_correlation(
    comparison["REALIZED"],
    comparison["GARCH"],
)


print("\nGARCH OOS RESULTS")
print("=================")

print("observations:", len(comparison))
print("mae:", mae)
print("rmse:", rmse)
print("correlation:", correlation)
print(
    "average_forecast:",
    comparison["GARCH"].mean(),
)
print(
    "average_realized:",
    comparison["REALIZED"].mean(),
)

print(
    "\nComparison start:",
    comparison.index.min(),
)

print(
    "Comparison end:",
    comparison.index.max(),
)