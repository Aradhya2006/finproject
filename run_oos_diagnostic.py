import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.forecasting.diebold_mariano import compare_models_dm
from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.forecasting.statistical_tests import compare_forecast_errors

from src.finance.portfolio import calculate_portfolio_returns

from src.forecasting.dl_preprocessing import (
    prepare_lstm_data,
)

from src.forecasting.evaluation_dataset import (
    create_oos_evaluation_dataset,
)

from src.forecasting.rolling import (
    calculate_rolling_volatility_forecast,
)

from src.forecasting.ewma import (
    calculate_ewma_volatility,
)

from src.forecasting.garch_oos import (
    generate_garch_oos_forecasts,
)

from src.forecasting.lstm_training import (
    train_lstm,
)

from src.forecasting.lstm_evaluation import (
    generate_lstm_predictions,
)


# ---------------------------------------------------------
# Portfolio A
# ---------------------------------------------------------

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
# Shared OOS dates
# ---------------------------------------------------------

data = prepare_lstm_data(
    portfolio_returns,
    lookback=60,
    horizon=21,
    test_months=6,
)

test_dates = data["dates_test"]


# ---------------------------------------------------------
# Shared realized target
# ---------------------------------------------------------

oos = create_oos_evaluation_dataset(
    portfolio_returns,
    test_dates,
    horizon=21,
)


# ---------------------------------------------------------
# Rolling
# ---------------------------------------------------------

rolling = calculate_rolling_volatility_forecast(
    portfolio_returns,
    window=21,
)

rolling = rolling.loc[test_dates]


# ---------------------------------------------------------
# EWMA
# ---------------------------------------------------------

ewma = (
    calculate_ewma_volatility(
        portfolio_returns,
        lambda_=0.94,
    )
    * np.sqrt(252)
)

ewma = ewma.loc[test_dates]


# ---------------------------------------------------------
# GARCH
# ---------------------------------------------------------

garch = generate_garch_oos_forecasts(
    portfolio_returns,
    test_dates,
    refit_frequency=21,
)


# ---------------------------------------------------------
# LSTM
# ---------------------------------------------------------

model, history = train_lstm(
    data["X_train"],
    data["y_train"],
    data["X_validation"],
    data["y_validation"],
    hidden_size=64,
    learning_rate=0.001,
    batch_size=32,
    epochs=100,
    patience=10,
)

lstm_predictions = generate_lstm_predictions(
    model,
    data["X_test"],
)

lstm = pd.Series(
    lstm_predictions,
    index=test_dates,
    name="LSTM",
)


# ---------------------------------------------------------
# Combine
# ---------------------------------------------------------

comparison = pd.DataFrame({
    "REALIZED": oos["REALIZED"],
    "ROLLING": rolling,
    "EWMA": ewma,
    "GARCH": garch,
    "LSTM": lstm,
}).dropna()

dm_results = compare_models_dm(
    comparison["REALIZED"],
    {
        "ROLLING": comparison["ROLLING"],
        "EWMA": comparison["EWMA"],
        "GARCH": comparison["GARCH"],
        "LSTM": comparison["LSTM"],
    },
    loss="squared",
)

print("\nDIEBOLD-MARIANO TEST")
print("====================")
print(dm_results.to_string(index=False))

# ---------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------

print("\nOOS DIAGNOSTIC SUMMARY")
print("======================")

print("\nAverage volatility:")
print(comparison.mean())

print("\nMinimum volatility:")
print(comparison.min())

print("\nMaximum volatility:")
print(comparison.max())

print("\nStandard deviation:")
print(comparison.std())

print("\nCorrelation matrix:")
print(comparison.corr().round(4))

error_comparison = compare_forecast_errors(
    comparison["REALIZED"],
    {
        "ROLLING": comparison["ROLLING"],
        "EWMA": comparison["EWMA"],
        "GARCH": comparison["GARCH"],
        "LSTM": comparison["LSTM"],
    },
)

print("\nFORECAST ERROR COMPARISON")
print("=========================")
print(error_comparison.to_string(index=False))
# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------

plt.figure(figsize=(14, 7))

plt.plot(
    comparison.index,
    comparison["REALIZED"],
    label="Realized",
    linewidth=2,
)

plt.plot(
    comparison.index,
    comparison["ROLLING"],
    label="Rolling",
)

plt.plot(
    comparison.index,
    comparison["EWMA"],
    label="EWMA",
)

plt.plot(
    comparison.index,
    comparison["GARCH"],
    label="GARCH",
)

plt.plot(
    comparison.index,
    comparison["LSTM"],
    label="LSTM",
)

plt.title(
    "OOS Volatility Forecast Comparison — Portfolio A"
)

plt.xlabel("Date")
plt.ylabel("Annualized Volatility")

plt.legend()
plt.grid(True)

plt.tight_layout()

plt.savefig(
    "oos_volatility_comparison.png",
    dpi=300,
)

# plt.show()