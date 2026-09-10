import numpy as np

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


def test_real_portfolio_a_lstm_features():

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

    # Load real NSE data
    price_data = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(
        price_data
    )

    # Portfolio return series
    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    portfolio_returns = (
        portfolio_returns
        .set_index("DATE")["PORTFOLIO RETURN"]
        .dropna()
    )

    # Create volatility features
    features = create_volatility_features(
        portfolio_returns,
        rolling_window=21,
        ewma_lambda=0.94,
    )

    # Create LSTM sequences
    X, y, dates = (
        create_lstm_feature_sequences(
            features,
            portfolio_returns,
            sequence_length=60,
            forecast_horizon=21,
        )
    )

    print("\nREAL PORTFOLIO A")
    print("=" * 50)

    print("Portfolio return observations:",
          len(portfolio_returns))

    print("Feature shape:",
          features.shape)

    print("Sequence shape:",
          X.shape)

    print("Target shape:",
          y.shape)

    print("First sequence date:",
          dates[0])

    print("Last sequence date:",
          dates[-1])

    print("Feature names:")
    print(list(features.columns))

    assert X.ndim == 3
    assert X.shape[1] == 60
    assert X.shape[2] == 5

    assert y.ndim == 1
    assert len(X) == len(y)
    assert len(X) == len(dates)

    assert np.all(np.isfinite(X))
    assert np.all(np.isfinite(y))

    print("\nReal Portfolio A feature sequence test successful")