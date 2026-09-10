import numpy as np
import pandas as pd


def calculate_error_series(actual, predicted):
    """
    Calculate forecast errors.

    Error = predicted - actual
    """

    actual = pd.Series(actual).reset_index(drop=True)
    predicted = pd.Series(predicted).reset_index(drop=True)

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted arrays must have "
            "the same length."
        )

    return predicted - actual


def calculate_absolute_error(actual, predicted):
    """
    Calculate absolute forecast errors.
    """

    errors = calculate_error_series(
        actual,
        predicted,
    )

    return errors.abs()


def calculate_squared_error(actual, predicted):
    """
    Calculate squared forecast errors.
    """

    errors = calculate_error_series(
        actual,
        predicted,
    )

    return errors ** 2


def compare_forecast_errors(
    actual,
    forecasts,
):
    """
    Compare forecasting models using MAE and RMSE.

    Parameters
    ----------
    actual : array-like
        Realized volatility.

    forecasts : dict
        Dictionary containing model name -> predictions.

    Returns
    -------
    pandas.DataFrame
        Error comparison table.
    """

    actual = pd.Series(actual).reset_index(drop=True)

    results = []

    for model_name, predicted in forecasts.items():

        predicted = pd.Series(
            predicted
        ).reset_index(drop=True)

        if len(actual) != len(predicted):
            raise ValueError(
                f"{model_name}: actual and predicted "
                "arrays must have the same length."
            )

        errors = predicted - actual

        mae = np.mean(
            np.abs(errors)
        )

        rmse = np.sqrt(
            np.mean(errors ** 2)
        )

        results.append(
            {
                "MODEL": model_name,
                "MAE": mae,
                "RMSE": rmse,
                "BIAS": np.mean(errors),
            }
        )

    return pd.DataFrame(results)