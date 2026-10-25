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


PORTFOLIO_A_WEIGHTS = {
    "TCS": 0.25,
    "INFY": 0.25,
    "HCLTECH": 0.20,
    "WIPRO": 0.15,
    "RELIANCE": 0.15,
}


def test_real_portfolio_a_lstm_training():

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
    # Verify split
    # -------------------------
    assert X_train.shape == (1969, 60)
    assert y_train.shape == (1969,)

    assert X_validation.shape == (422, 60)
    assert y_validation.shape == (422,)

    assert X_test.shape == (423, 60)
    assert y_test.shape == (423,)

    assert train_dates[-1] < validation_dates[0]
    assert validation_dates[-1] < test_dates[0]

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
    # Verify scaled shapes
    # -------------------------
    assert X_train_scaled.shape == (1969, 60)
    assert X_validation_scaled.shape == (422, 60)
    assert X_test_scaled.shape == (423, 60)

    # -------------------------
    # Print information
    # -------------------------
    print("\nPortfolio A LSTM training")
    print("=" * 50)

    print("\nSHAPES BEFORE TRAINING")

    print("X_train:", X_train.shape)
    print("y_train:", y_train.shape)

    print("X_validation:", X_validation.shape)
    print("y_validation:", y_validation.shape)

    print("X_test:", X_test.shape)
    print("y_test:", y_test.shape)

    print("\nSCALED SHAPES")

    print(
        "X_train_scaled:",
        X_train_scaled.shape,
    )

    print(
        "X_validation_scaled:",
        X_validation_scaled.shape,
    )

    print(
        "X_test_scaled:",
        X_test_scaled.shape,
    )

    print("\nDATE RANGES")

    print(
        "Training:",
        train_dates[0],
        "->",
        train_dates[-1],
    )

    print(
        "Validation:",
        validation_dates[0],
        "->",
        validation_dates[-1],
    )

    print(
        "Test:",
        test_dates[0],
        "->",
        test_dates[-1],
    )

    print("\nSCALED DATA")

    print(
        "Training mean:",
        np.mean(X_train_scaled),
    )

    print(
        "Training std:",
        np.std(X_train_scaled),
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
    # Validate training history
    # -------------------------
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
    # Test predictions
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

    assert predictions.shape == (
        len(X_test),
    )

    assert torch.isfinite(
        predictions
    ).all()

    # -------------------------
    # Final results
    # -------------------------
    print(
        "\nFinal training loss:",
        f"{history['train_loss'][-1]:.6f}",
    )

    print(
        "Final validation loss:",
        f"{history['validation_loss'][-1]:.6f}",
    )

    print(
        "\nReal Portfolio A LSTM training successful"
    )