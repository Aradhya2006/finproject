import numpy as np
import pandas as pd

def create_lstm_sequences(
    returns,
    sequence_length=60,
    forecast_horizon=21,
):
    if not isinstance(returns, pd.Series):
        raise ValueError(
            "returns must be a pandas Series."
        )

    if returns.empty:
        raise ValueError(
            "returns cannot be empty."
        )

    if sequence_length <= 0:
        raise ValueError(
            "sequence_length must be positive."
        )

    if forecast_horizon <= 0:
        raise ValueError(
            "forecast_horizon must be positive."
        )

    data = returns.dropna()

    required_length = (
        sequence_length + forecast_horizon
    )

    if len(data) < required_length:
        raise ValueError(
            "Not enough observations to create "
            "sequences."
        )

    values = data.to_numpy(
        dtype=float
    )

    dates = data.index

    X = []
    y = []
    sequence_dates = []

    for i in range(
        len(values) - required_length + 1
    ):

        input_end = (
            i + sequence_length
        )

        target_end = (
            input_end + forecast_horizon
        )

        input_sequence = values[
            i:input_end
        ]

        future_returns = values[
            input_end:target_end
        ]

        realized_volatility = (
            np.std(
                future_returns,
                ddof=1,
            )
            * np.sqrt(252)
        )

        X.append(input_sequence)

        y.append(
            realized_volatility
        )

        sequence_dates.append(
            dates[input_end - 1]
        )

    X = np.array(
        X,
        dtype=np.float32,
    )

    y = np.array(
        y,
        dtype=np.float32,
    )

    sequence_dates = pd.DatetimeIndex(
        sequence_dates
    )

    return (
        X,
        y,
        sequence_dates,
    )


def create_lstm_feature_sequences(
    features,
    target_returns,
    sequence_length=60,
    forecast_horizon=21,
):
    if not isinstance(features, pd.DataFrame):
        raise ValueError(
            "features must be a pandas DataFrame."
        )

    if not isinstance(target_returns, pd.Series):
        raise ValueError(
            "target_returns must be a pandas Series."
        )

    if features.empty:
        raise ValueError(
            "features cannot be empty."
        )

    if target_returns.empty:
        raise ValueError(
            "target_returns cannot be empty."
        )

    if sequence_length <= 0:
        raise ValueError(
            "sequence_length must be positive."
        )

    if forecast_horizon <= 0:
        raise ValueError(
            "forecast_horizon must be positive."
        )

    if not features.index.equals(target_returns.index):
        raise ValueError(
            "features and target_returns must have "
            "the same index."
        )

    # Remove rows where feature calculations
    # are not yet available.
    valid_features = features.dropna()

    if valid_features.empty:
        raise ValueError(
            "No valid feature rows remain after "
            "removing NaNs."
        )

    # Keep target returns aligned with the
    # remaining feature dates.
    valid_returns = target_returns.loc[
        valid_features.index
    ]

    required_length = (
        sequence_length + forecast_horizon
    )

    if len(valid_features) < required_length:
        raise ValueError(
            "Not enough observations to create "
            "sequences."
        )

    feature_values = valid_features.to_numpy(
        dtype=np.float32
    )

    return_values = valid_returns.to_numpy(
        dtype=float
    )

    dates = valid_features.index

    X = []
    y = []
    sequence_dates = []

    for i in range(
        len(feature_values) - required_length + 1
    ):
        input_end = i + sequence_length
        target_end = (
            input_end + forecast_horizon
        )

        input_sequence = feature_values[
            i:input_end
        ]

        future_returns = return_values[
            input_end:target_end
        ]

        realized_volatility = (
            np.std(
                future_returns,
                ddof=1,
            )
            * np.sqrt(252)
        )

        X.append(input_sequence)
        y.append(realized_volatility)

        # Date corresponding to the last
        # observation available to the model.
        sequence_dates.append(
            dates[input_end - 1]
        )

    X = np.array(
        X,
        dtype=np.float32,
    )

    y = np.array(
        y,
        dtype=np.float32,
    )

    sequence_dates = pd.DatetimeIndex(
        sequence_dates
    )

    return X, y, sequence_dates