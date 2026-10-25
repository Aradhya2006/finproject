import numpy as np

from src.finance.dataset import create_price_dataset, calculate_asset_returns
from src.finance.portfolio import calculate_portfolio_returns
from src.forecasting.lstm_dataset import create_lstm_sequences


PORTFOLIO_A_WEIGHTS = {
    "TCS": 0.25,
    "INFY": 0.25,
    "HCLTECH": 0.20,
    "WIPRO": 0.15,
    "RELIANCE": 0.15,
}


def test_real_portfolio_a_lstm_dataset():
    symbols = list(PORTFOLIO_A_WEIGHTS.keys())

    price_data = create_price_dataset(symbols)
    asset_returns = calculate_asset_returns(price_data)

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        PORTFOLIO_A_WEIGHTS,
    )

    returns = portfolio_returns.set_index("DATE")["PORTFOLIO RETURN"]
    X, y, dates = create_lstm_sequences(
        returns,
        sequence_length=60,
        forecast_horizon=21,
    )

    print("\nPortfolio A LSTM dataset")
    print("=" * 40)
    print("Original return observations:", len(returns))
    print("Sequences:", len(X))
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print("First sequence date:", dates[0])
    print("Last sequence date:", dates[-1])
    print("NaNs in X:", np.isnan(X).sum())
    print("NaNs in y:", np.isnan(y).sum())

    assert len(X) == len(y)
    assert len(X) == len(dates)

    assert X.shape[1] == 60
    assert y.ndim == 1

    assert not np.isnan(X).any()
    assert not np.isnan(y).any()

    assert dates.is_monotonic_increasing

    assert np.all(y >= 0)