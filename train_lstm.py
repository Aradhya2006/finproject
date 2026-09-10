from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
import numpy as np
from src.forecasting.evaluation_dataset import (
    create_oos_evaluation_dataset,
)

from src.forecasting.lstm_evaluation import (
    generate_lstm_predictions,
    evaluate_lstm_predictions,
)

from src.finance.portfolio import calculate_portfolio_returns

from src.forecasting.dl_preprocessing import prepare_lstm_data
from src.forecasting.lstm_training import train_lstm


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
# Prepare leakage-free datasets
# ---------------------------------------------------------

data = prepare_lstm_data(
    portfolio_returns,
    lookback=60,
    horizon=21,
    test_months=6,
)


# ---------------------------------------------------------
# Train LSTM
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


print("\nTraining complete.")
print("Best validation loss:",
      min(history["validation_loss"]))

print("Epochs trained:",
      len(history["train_loss"]))


best_epoch = history["validation_loss"].index(
    min(history["validation_loss"])
) + 1

print("Best epoch:", best_epoch)
print("Final training loss:", history["train_loss"][-1])
print("Final validation loss:", history["validation_loss"][-1])


# ---------------------------------------------------------
# Locked OOS test
# ---------------------------------------------------------

test_predictions = generate_lstm_predictions(
    model,
    data["X_test"],
)
# Convert predictions from log-volatility
# back to ordinary volatility.
test_predictions = np.exp(test_predictions)
# Use the shared OOS realized-volatility target
oos_dataset = create_oos_evaluation_dataset(
    portfolio_returns,
    data["dates_test"],
    horizon=21,
)

test_results = evaluate_lstm_predictions(
    oos_dataset["REALIZED"].to_numpy(),
    test_predictions,
)

print("\nLSTM OOS TEST RESULTS")
print("---------------------")

for key, value in test_results.items():
    print(f"{key}: {value}")