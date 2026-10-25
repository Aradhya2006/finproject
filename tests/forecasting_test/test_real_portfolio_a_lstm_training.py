import numpy as np
import torch

from src.finance.dataset import create_price_dataset, calculate_asset_returns
from src.finance.portfolio import calculate_portfolio_returns
from src.forecasting.lstm_dataset import create_lstm_sequences
from src.forecasting.split import chronological_split
from src.forecasting.scaler import StandardScaler
from src.forecasting.lstm_model import LSTMVolatilityModel
from src.forecasting.trainer import train_lstm


def test_real_portfolio_a_lstm_training():

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

    # -------------------------
    # Load real NSE data
    # -------------------------
    price_data = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(price_data)

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
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

    X_train_scaled = scaler.fit_transform(X_train)

    X_validation_scaled = scaler.transform(
        X_validation
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    # -------------------------
    # DEBUG: Check shapes
    # -------------------------
    print("\nSHAPES BEFORE TRAINING")
    print("X_train:", X_train.shape)
    print("y_train:", y_train.shape)
    print("X_validation:", X_validation.shape)
    print("y_validation:", y_validation.shape)
    print("X_test:", X_test.shape)
    print("y_test:", y_test.shape)

    print("\nSCALED SHAPES")
    print("X_train_scaled:", X_train_scaled.shape)
    print("X_validation_scaled:", X_validation_scaled.shape)
    print("X_test_scaled:", X_test_scaled.shape)

    print("\nVALUES")
    print(
        "X_validation_scaled min:",
        np.min(X_validation_scaled),
    )
    print(
        "X_validation_scaled max:",
        np.max(X_validation_scaled),
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
        epochs=3,
        learning_rate=0.001,
    )

    # -------------------------
    # Basic validation
    # -------------------------
    assert len(X_train) > 1000
    assert len(X_validation) > 100
    assert len(X_test) > 100

    assert X_train_scaled.shape == X_train.shape
    assert X_validation_scaled.shape == X_validation.shape
    assert X_test_scaled.shape == X_test.shape

    assert len(history["train_loss"]) == 3
    assert len(history["validation_loss"]) == 3

    assert all(
        np.isfinite(loss)
        for loss in history["train_loss"]
    )

    assert all(
        np.isfinite(loss)
        for loss in history["validation_loss"]
    )

    # -------------------------
    # Test prediction
    # -------------------------
    model.eval()

    with torch.no_grad():
        test_tensor = torch.tensor(
            X_test_scaled,
            dtype=torch.float32,
        ).unsqueeze(-1)

        predictions = trained_model(test_tensor)

    assert predictions.shape == (
        len(X_test),
    )

    assert torch.isfinite(predictions).all()

    print("\nReal Portfolio A LSTM training successful")
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_validation)}")
    print(f"Test samples: {len(X_test)}")
    print(
        f"Final training loss: "
        f"{history['train_loss'][-1]:.6f}"
    )
    print(
        f"Final validation loss: "
        f"{history['validation_loss'][-1]:.6f}"
    )
