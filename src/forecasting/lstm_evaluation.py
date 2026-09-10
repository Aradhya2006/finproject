import numpy as np
import pandas as pd
import torch

from src.forecasting.evaluation import (
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
)


def generate_lstm_predictions(model, X):
    if X.ndim != 3:
        raise ValueError(
            "X must have shape "
            "(samples, sequence_length, features)."
        )

    model.eval()

    X_tensor = torch.tensor(
        X,
        dtype=torch.float32,
    )

    with torch.no_grad():
        predictions = model(X_tensor)

    return predictions.cpu().numpy()


def evaluate_lstm_predictions(
    y_actual,
    y_predicted,
):
    y_actual = np.asarray(y_actual)
    y_predicted = np.asarray(y_predicted)

    if len(y_actual) != len(y_predicted):
        raise ValueError(
            "Actual and predicted arrays must have "
            "the same length."
        )

    actual = pd.Series(y_actual)
    predicted = pd.Series(y_predicted)

    return {
        "observations": len(y_actual),
        "mae": calculate_mae(
            actual,
            predicted,
        ),
        "rmse": calculate_rmse(
            actual,
            predicted,
        ),
        "correlation": calculate_forecast_correlation(
            actual,
            predicted,
        ),
        "average_forecast": float(
            np.mean(y_predicted)
        ),
        "average_realized": float(
            np.mean(y_actual)
        ),
    }