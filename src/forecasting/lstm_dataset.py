import numpy as np


def create_lstm_sequences(
    returns,
    sequence_length=60,
    forecast_horizon=21,
):
    """
    Create sequences for volatility forecasting.

    X:
        Previous `sequence_length` daily returns.

    y:
        Annualized realized volatility over the next
        `forecast_horizon` trading days.
    """

    returns = np.asarray(returns, dtype=float)

    if returns.ndim != 1:
        raise ValueError("returns must be a one-dimensional array.")

    if sequence_length <= 0:
        raise ValueError("sequence_length must be greater than zero.")

    if forecast_horizon <= 1:
        raise ValueError("forecast_horizon must be greater than one.")

    returns = returns[~np.isnan(returns)]

    required_length = sequence_length + forecast_horizon

    if len(returns) < required_length:
        raise ValueError(
            "Not enough returns for the selected sequence length "
            "and forecast horizon."
        )

    X = []
    y = []

    for i in range(len(returns) - required_length + 1):
        input_end = i + sequence_length
        target_end = input_end + forecast_horizon

        input_sequence = returns[i:input_end]
        future_returns = returns[input_end:target_end]

        realized_volatility = (
            np.std(future_returns, ddof=1) * np.sqrt(252)
        )

        X.append(input_sequence)
        y.append(realized_volatility)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    return X, y