import numpy as np


def calculate_lstm_metrics(
    predictions,
    actual,
):
    predictions = np.asarray(predictions, dtype=float)
    actual = np.asarray(actual, dtype=float)

    if len(predictions) != len(actual):
        raise ValueError(
            "predictions and actual must have the same length."
        )

    if len(predictions) == 0:
        raise ValueError(
            "predictions and actual cannot be empty."
        )

    if not np.all(np.isfinite(predictions)):
        raise ValueError(
            "predictions contain non-finite values."
        )

    if not np.all(np.isfinite(actual)):
        raise ValueError(
            "actual contains non-finite values."
        )

    errors = predictions - actual

    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors ** 2))

    if np.std(predictions) == 0 or np.std(actual) == 0:
        correlation = np.nan
    else:
        correlation = np.corrcoef(
            predictions,
            actual,
        )[0, 1]

    return {
        "MAE": mae,
        "RMSE": rmse,
        "CORR": correlation,
    }