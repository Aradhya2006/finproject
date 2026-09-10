import numpy as np
import pandas as pd
from scipy.stats import t


def diebold_mariano_test(
    actual,
    forecast_1,
    forecast_2,
    loss="squared",
):
    """
    Diebold-Mariano test for comparing two forecast models.

    H0:
        The two forecasting models have equal predictive accuracy.

    H1:
        The two forecasting models have different predictive accuracy.

    Parameters
    ----------
    actual : array-like
        Realized volatility.

    forecast_1 : array-like
        Forecasts from model 1.

    forecast_2 : array-like
        Forecasts from model 2.

    loss : str
        Loss function:
            "absolute" -> absolute error
            "squared"  -> squared error

    Returns
    -------
    dict
        DM statistic and p-value.
    """

    actual = np.asarray(actual, dtype=float)
    forecast_1 = np.asarray(forecast_1, dtype=float)
    forecast_2 = np.asarray(forecast_2, dtype=float)

    if not (
        len(actual)
        == len(forecast_1)
        == len(forecast_2)
    ):
        raise ValueError(
            "Actual and forecast arrays must "
            "have the same length."
        )

    if len(actual) < 3:
        raise ValueError(
            "At least 3 observations are required."
        )

    if loss == "absolute":

        loss_1 = np.abs(
            actual - forecast_1
        )

        loss_2 = np.abs(
            actual - forecast_2
        )

    elif loss == "squared":

        loss_1 = (
            actual - forecast_1
        ) ** 2

        loss_2 = (
            actual - forecast_2
        ) ** 2

    else:
        raise ValueError(
            "loss must be 'absolute' or 'squared'."
        )

    # Loss differential
    d = loss_1 - loss_2

    n = len(d)
    mean_d = np.mean(d)

    # Variance of the loss differential.
    # For a one-step forecast comparison,
    # the basic DM statistic uses the sample variance.
    variance_d = np.var(
        d,
        ddof=1,
    )

    if variance_d == 0:
        raise ValueError(
            "Loss differential has zero variance."
        )

    dm_statistic = (
        mean_d
        / np.sqrt(variance_d / n)
    )

    # Small-sample correction
    correction = np.sqrt(
        (n + 1 - 2 + 1) / n
    )

    dm_statistic *= correction

    degrees_of_freedom = n - 1

    p_value = 2 * (
        1
        - t.cdf(
            abs(dm_statistic),
            df=degrees_of_freedom,
        )
    )

    return {
        "observations": n,
        "dm_statistic": float(dm_statistic),
        "p_value": float(p_value),
        "loss": loss,
    }


def compare_models_dm(
    actual,
    forecasts,
    loss="squared",
):
    """
    Run pairwise Diebold-Mariano tests
    across all forecasting models.
    """

    model_names = list(forecasts.keys())

    results = []

    for i in range(len(model_names)):

        for j in range(i + 1, len(model_names)):

            model_1 = model_names[i]
            model_2 = model_names[j]

            result = diebold_mariano_test(
                actual,
                forecasts[model_1],
                forecasts[model_2],
                loss=loss,
            )

            results.append(
                {
                    "MODEL 1": model_1,
                    "MODEL 2": model_2,
                    "DM STATISTIC": result[
                        "dm_statistic"
                    ],
                    "P-VALUE": result[
                        "p_value"
                    ],
                }
            )

    return pd.DataFrame(results)