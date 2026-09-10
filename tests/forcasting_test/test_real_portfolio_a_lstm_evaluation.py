import numpy as np
import torch

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import calculate_portfolio_returns
from src.forecasting.lstm_dataset import create_lstm_sequences
from src.forecasting.split import chronological_split
from src.forecasting.scaler import StandardScaler
from src.forecasting.lstm_model import LSTMVolatilityModel
from src.forecasting.trainer import train_lstm
from src.forecasting.lstm_evaluation import (
    calculate_lstm_metrics,
)


PORTFOLIO_A_WEIGHTS = {
    "TCS": 0.25,
    "INFY": 0.25,
    "HCLTECH": 0.20,
    "WIPRO": 0.15,
    "RELIANCE": 0.15,
}


def test_real_portfolio_a_lstm_evaluation():

    # -------------------------
    # Load real NSE data
    # -------------------------
    symbols = list(PORTFOLIO_A_WEIGHTS.keys())

    price_data = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(
        price_data
    )

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        PORTFOLIO_A_WEIGHTS,
    )

    returns = portfolio_returns.set_index("DATE")[
        "PORTFOLIO RETURN"
    ]

    # -------------------------
    # Create LSTM sequences
    # -------------------------
    X, y, dates = create_lstm_sequences(
        returns,
        sequence_length=60,
        forecast_horizon=21,
    )

    # -------------------------
    # Chronological split
    # -------------------------
    (
        X_train,
        y_train,
        train_dates,
        X_validation,
        y_validation,
        validation_dates,
        X_test,
        y_test,
        test_dates,
    ) = chronological_split(
        X,
        y,
        dates,
        train_ratio=0.70,
        validation_ratio=0.15,
    )

    # -------------------------
    # Scale using TRAINING data
    # -------------------------
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_validation_scaled = scaler.transform(
        X_validation
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    # -------------------------
    # Train LSTM
    # -------------------------
    model = LSTMVolatilityModel()

    trained_model, history = train_lstm(
    model,
    X_train_scaled,
    y_train,
    X_validation_scaled,
    y_validation,
    epochs=50,
    learning_rate=0.001,
    patience=7,
)

    # -------------------------
    # Generate test predictions
    # -------------------------
    trained_model.eval()

    test_tensor = torch.tensor(
        X_test_scaled,
        dtype=torch.float32,
    ).unsqueeze(-1)

    with torch.no_grad():
        predictions = trained_model(
            test_tensor
        )

    predictions = predictions.numpy()

    # -------------------------
    # Calculate test metrics
    # -------------------------
    metrics = calculate_lstm_metrics(
        predictions,
        y_test,
    )

    # -------------------------
    # Validate results
    # -------------------------
    assert predictions.shape == y_test.shape

    assert np.isfinite(
        predictions
    ).all()

    assert np.isfinite(
        metrics["MAE"]
    )

    assert np.isfinite(
        metrics["RMSE"]
    )

    assert np.isfinite(
        metrics["CORR"]
    )

    # Volatility cannot be negative
    assert np.all(
        predictions >= 0
    )

    # -------------------------
    # Print results
    # -------------------------
    print("\nTRAINING SUMMARY")
    print("=" * 50)

    print(
        "Epochs trained:",
        history["epochs_trained"],
    )

    print(
        "Best validation loss:",
        f"{history['best_validation_loss']:.6f}",
    )
    print("\nReal Portfolio A LSTM Evaluation")
    print("=" * 50)

    print("\nTEST PERIOD")

    print(
        "Start:",
        test_dates[0],
    )

    print(
        "End:",
        test_dates[-1],
    )

    print(
        "Observations:",
        len(y_test),
    )

    print("\nPERFORMANCE")

    print(
        "MAE:",
        f"{metrics['MAE']:.6f}",
    )

    print(
        "RMSE:",
        f"{metrics['RMSE']:.6f}",
    )

    print(
        "Correlation:",
        f"{metrics['CORR']:.6f}",
    )

    print("\nAVERAGE VOLATILITY")

    print(
        "Predicted:",
        f"{np.mean(predictions):.6f}",
    )

    print(
        "Actual:",
        f"{np.mean(y_test):.6f}",
    )

    print(
        "\nReal Portfolio A LSTM evaluation successful"
    )