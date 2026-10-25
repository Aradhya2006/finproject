import numpy as np
import torch

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import (
    calculate_portfolio_returns,
)
from src.forecasting.lstm_dataset import (
    create_lstm_sequences,
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


def test_common_baseline_lstm():
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

    # -----------------------------------------
    # 1. Load Portfolio A
    # -----------------------------------------

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
        .set_index("DATE")[
            "PORTFOLIO RETURN"
        ]
        .dropna()
    )

    # -----------------------------------------
    # 2. Create baseline LSTM sequences
    # -----------------------------------------

    X, y, dates = create_lstm_sequences(
        portfolio_returns,
        sequence_length=60,
        forecast_horizon=21,
    )

    # -----------------------------------------
    # 3. Chronological split
    # -----------------------------------------

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

    # -----------------------------------------
    # 4. Scale using training data only
    # -----------------------------------------

    scaler = StandardScaler()

    scaler.fit(X_train)

    X_train_scaled = scaler.transform(
        X_train
    )

    X_validation_scaled = scaler.transform(
        X_validation
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    # -----------------------------------------
    # 5. We need the exact common period
    # -----------------------------------------

    common_start = (
        "2024-11-27"
    )

    common_end = (
        "2026-08-06"
    )

    common_mask = (
        (test_dates >= common_start)
        & (test_dates <= common_end)
    )

    X_test_common = X_test_scaled[
        common_mask
    ]

    y_test_common = y_test[
        common_mask
    ]

    dates_test_common = test_dates[
        common_mask
    ]

    # -----------------------------------------
    # 6. Train baseline LSTM
    # -----------------------------------------

    model = LSTMVolatilityModel(
        input_size=1,
        hidden_size=32,
        num_layers=2,
        dropout=0.2,
    )

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

    # -----------------------------------------
    # 7. Predict common test period
    # -----------------------------------------

    test_tensor = torch.tensor(
    X_test_common,
    dtype=torch.float32,
).unsqueeze(-1)

    trained_model.eval()

    with torch.no_grad():
        predictions = (
            trained_model(test_tensor)
            .cpu()
            .numpy()
        )

    # -----------------------------------------
    # 8. Metrics
    # -----------------------------------------

    metrics = calculate_lstm_metrics(
        predictions,
        y_test_common,
    )

    print(
        "\nCOMMON BASELINE LSTM"
    )
    print("=" * 60)

    print(
        "Start:",
        dates_test_common[0],
    )

    print(
        "End:",
        dates_test_common[-1],
    )

    print(
        "Observations:",
        len(y_test_common),
    )

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

    print(
        "Average forecast:",
        f"{np.mean(predictions):.6f}",
    )

    print(
        "Average realized:",
        f"{np.mean(y_test_common):.6f}",
    )

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    assert len(y_test_common) == 420
    assert len(predictions) == 420

    assert np.all(
        np.isfinite(predictions)
    )

    assert np.isfinite(
        metrics["MAE"]
    )

    assert np.isfinite(
        metrics["RMSE"]
    )

    print(
        "\nCommon baseline LSTM "
        "comparison successful"
    )