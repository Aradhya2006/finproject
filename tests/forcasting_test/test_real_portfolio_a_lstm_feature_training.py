import numpy as np
import torch

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import (
    calculate_portfolio_returns,
)
from src.forecasting.lstm_features import (
    create_volatility_features,
)
from src.forecasting.lstm_dataset import (
    create_lstm_feature_sequences,
)
from src.forecasting.split import (
    chronological_split,
)
from src.forecasting.scaler import (
    StandardScaler,
)
from src.forecasting.lstm_model import (
    LSTMVolatilityModel,
)
from src.forecasting.trainer import (
    train_lstm,
)


def test_real_portfolio_a_lstm_feature_training():

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

    # --------------------------------------------------
    # 1. Load real NSE data
    # --------------------------------------------------

    price_data = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(
        price_data
    )

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    portfolio_returns = (
        portfolio_returns
        .set_index("DATE")["PORTFOLIO RETURN"]
        .dropna()
    )

    # --------------------------------------------------
    # 2. Create volatility features
    # --------------------------------------------------

    features = create_volatility_features(
        portfolio_returns,
        rolling_window=21,
        ewma_lambda=0.94,
    )

    # --------------------------------------------------
    # 3. Create sequences
    # --------------------------------------------------

    X, y, dates = (
        create_lstm_feature_sequences(
            features,
            portfolio_returns,
            sequence_length=60,
            forecast_horizon=21,
        )
    )

    # --------------------------------------------------
    # 4. Chronological split
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 5. Scale using TRAINING data only
    # --------------------------------------------------

    scaler = StandardScaler()

    X_train_2d = X_train.reshape(
        -1,
        X_train.shape[-1],
    )

    scaler.fit(X_train_2d)

    X_train_scaled = scaler.transform(
        X_train_2d
    ).reshape(X_train.shape)

    X_validation_scaled = scaler.transform(
        X_validation.reshape(
            -1,
            X_validation.shape[-1],
        )
    ).reshape(X_validation.shape)

    X_test_scaled = scaler.transform(
        X_test.reshape(
            -1,
            X_test.shape[-1],
        )
    ).reshape(X_test.shape)

    # --------------------------------------------------
    # 6. Build enhanced LSTM
    # --------------------------------------------------

    model = LSTMVolatilityModel(
        input_size=5,
        hidden_size=32,
        num_layers=2,
        dropout=0.2,
    )

    # --------------------------------------------------
    # 7. Train
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 8. Basic validation
    # --------------------------------------------------

    assert X_train_scaled.shape[2] == 5
    assert X_validation_scaled.shape[2] == 5
    assert X_test_scaled.shape[2] == 5

    assert len(history["train_loss"]) > 0
    assert len(history["validation_loss"]) > 0

    assert np.isfinite(
        history["best_validation_loss"]
    )

    # Verify model can process the enhanced
    # 3-dimensional input.
    test_tensor = torch.tensor(
        X_test_scaled[:8],
        dtype=torch.float32,
    )

    trained_model.eval()

    with torch.no_grad():
        predictions = trained_model(
            test_tensor
        )

    assert predictions.shape == (8,)
    assert torch.isfinite(predictions).all()

    print("\nENHANCED LSTM TRAINING")
    print("=" * 50)

    print(
        "Training samples:",
        len(X_train),
    )

    print(
        "Validation samples:",
        len(X_validation),
    )

    print(
        "Test samples:",
        len(X_test),
    )

    print(
        "Input shape:",
        X_train_scaled.shape,
    )

    print(
        "Features:",
        X_train_scaled.shape[2],
    )

    print(
        "Epochs trained:",
        history["epochs_trained"],
    )

    print(
        "Best validation loss:",
        f"{history['best_validation_loss']:.6f}",
    )

    print(
        "\nEnhanced Real Portfolio A "
        "LSTM training successful"
    )