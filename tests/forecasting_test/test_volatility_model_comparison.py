import numpy as np
import pandas as pd

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


def test_common_volatility_evaluation_period():

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
    # Load Portfolio A
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
        .set_index("DATE")["PORTFOLIO RETURN"]
        .dropna()
    )

    # -----------------------------------------
    # Create enhanced LSTM features
    # -----------------------------------------

    features = create_volatility_features(
        portfolio_returns,
        rolling_window=21,
        ewma_lambda=0.94,
    )

    X, y, dates = (
        create_lstm_feature_sequences(
            features,
            portfolio_returns,
            sequence_length=60,
            forecast_horizon=21,
        )
    )

    # -----------------------------------------
    # Use the same final test period
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
    ) = (
        __import__(
            "src.forecasting.split",
            fromlist=["chronological_split"],
        ).chronological_split(
            X,
            y,
            dates,
            train_ratio=0.70,
            validation_ratio=0.15,
        )
    )

    common_start = test_dates[0]
    common_end = test_dates[-1]

    # -----------------------------------------
    # Extract exactly the same return period
    # -----------------------------------------

    common_returns = portfolio_returns.loc[
        common_start:common_end
    ]

    print("\nCOMMON VOLATILITY EVALUATION")
    print("=" * 50)

    print(
        "Common start:",
        common_start,
    )

    print(
        "Common end:",
        common_end,
    )

    print(
        "LSTM observations:",
        len(y_test),
    )

    print(
        "Return observations:",
        len(common_returns),
    )

    print(
        "LSTM input shape:",
        X_test.shape,
    )

    print(
        "LSTM target shape:",
        y_test.shape,
    )

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    assert len(y_test) == len(test_dates)

    assert len(common_returns) > 0

    assert X_test.shape[1] == 60
    assert X_test.shape[2] == 5

    assert np.all(
        np.isfinite(y_test)
    )

    print(
        "\nCommon evaluation period "
        "constructed successfully"
    )