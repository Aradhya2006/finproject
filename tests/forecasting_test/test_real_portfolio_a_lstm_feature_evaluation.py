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
from src.forecasting.lstm_evaluation import (
    calculate_lstm_metrics,
)


def test_real_portfolio_a_lstm_feature_evaluation():
    torch.manual_seed(42)
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
    # 1. Load real Portfolio A data
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
    # 2. Create five volatility features
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
    # 5. Scale using training data only
    # --------------------------------------------------

    scaler = StandardScaler()

    scaler.fit(
        X_train.reshape(
            -1,
            X_train.shape[-1],
        )
    )

    X_train_scaled = scaler.transform(
        X_train.reshape(
            -1,
            X_train.shape[-1],
        )
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
    # 6. Create enhanced LSTM
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
    # 8. Test prediction
    # --------------------------------------------------

    test_tensor = torch.tensor(
        X_test_scaled,
        dtype=torch.float32,
    )

    trained_model.eval()

    with torch.no_grad():
        predictions = (
            trained_model(test_tensor)
            .cpu()
            .numpy()
        )

    # --------------------------------------------------
    # 9. Calculate metrics
    # --------------------------------------------------

    metrics = calculate_lstm_metrics(
        predictions,
        y_test,
    )

    # --------------------------------------------------
    # 10. Validate results
    # --------------------------------------------------

    assert len(predictions) == len(y_test)

    assert np.all(
        np.isfinite(predictions)
    )

    assert np.all(
        np.isfinite(y_test)
    )

    assert np.isfinite(
        metrics["MAE"]
    )

    assert np.isfinite(
        metrics["RMSE"]
    )

    print("\nENHANCED LSTM EVALUATION")
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
        "\nEnhanced Real Portfolio A "
        "LSTM evaluation successful"
    )