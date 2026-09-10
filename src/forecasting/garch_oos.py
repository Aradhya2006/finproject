import numpy as np
import pandas as pd

from arch import arch_model


def generate_garch_oos_forecasts(
    returns,
    test_dates,
    horizon=21,
    refit_frequency=21,
):
    """
    Generate horizon-matched GARCH(1,1) volatility forecasts.

    At prediction date t:
        - information through t is available
        - GARCH parameters are periodically refitted
        - volatility is forecast for the next `horizon`
          trading days
        - the forecast is expressed as annualized volatility

    The forecast is calculated as:

        sqrt(mean(v_1, ..., v_h)) * sqrt(252)

    where v_h is the forecast conditional variance for
    each future trading day.

    Parameters are refitted every `refit_frequency` trading days.

    Parameters
    ----------
    returns : pandas.Series
        Daily portfolio returns indexed by date.

    test_dates : pandas.DatetimeIndex
        Dates on which forecasts are generated.

    horizon : int
        Number of future trading days to forecast.

    refit_frequency : int
        Number of prediction days between GARCH refits.

    Returns
    -------
    pandas.Series
        Annualized horizon-matched GARCH volatility forecasts.
    """

    returns = returns.dropna().copy()
    test_dates = pd.DatetimeIndex(test_dates)

    if horizon <= 0:
        raise ValueError(
            "horizon must be greater than zero."
        )

    if refit_frequency <= 0:
        raise ValueError(
            "refit_frequency must be greater than zero."
        )

    valid_dates = [
        date
        for date in test_dates
        if date in returns.index
    ]

    if not valid_dates:
        raise ValueError(
            "No test dates found in returns index."
        )

    forecasts = pd.Series(
        index=valid_dates,
        dtype=float,
        name="GARCH",
    )

    omega = None
    alpha = None
    beta = None
    variance = None

    for i, date in enumerate(valid_dates):

        position = returns.index.get_loc(date)

        # -------------------------------------------------
        # Refit GARCH parameters periodically
        # -------------------------------------------------

        if i % refit_frequency == 0:

            training_returns = returns.iloc[:position + 1]

            if len(training_returns) < 252:
                raise ValueError(
                    "At least 252 observations are required."
                )

            scaled_returns = training_returns * 100

            model = arch_model(
                scaled_returns,
                mean="Constant",
                vol="GARCH",
                p=1,
                q=1,
                dist="normal",
                rescale=False,
            )

            result = model.fit(
                disp="off"
            )

            omega = float(
                result.params["omega"]
            )

            alpha = float(
                result.params["alpha[1]"]
            )

            beta = float(
                result.params["beta[1]"]
            )

            # -------------------------------------------------
            # Generate a 21-day-ahead forecast directly from
            # the fitted model.
            # -------------------------------------------------

            variance_forecast = (
                result
                .forecast(horizon=horizon)
                .variance
                .iloc[-1]
                .to_numpy()
            )

        else:

            # -------------------------------------------------
            # Update today's conditional variance using the
            # observed return at date t.
            #
            # This gives the variance forecast for t+1.
            # -------------------------------------------------

            current_return = (
                returns.loc[date] * 100
            )

            variance = (
                omega
                + alpha * current_return ** 2
                + beta * variance
            )

            # -------------------------------------------------
            # Recursively forecast the following horizon.
            #
            # For h >= 2, expected squared return equals the
            # forecast variance, giving:
            #
            # v_h = omega + (alpha + beta) * v_(h-1)
            # -------------------------------------------------

            variance_forecast = np.empty(
                horizon,
                dtype=float,
            )

            variance_forecast[0] = variance

            for h in range(1, horizon):

                variance_forecast[h] = (
                    omega
                    + (alpha + beta)
                    * variance_forecast[h - 1]
                )

        # -------------------------------------------------
        # Store the horizon-matched annualized volatility.
        # -------------------------------------------------

        average_variance = np.mean(
            variance_forecast
        )

        annualized_volatility = (
            np.sqrt(average_variance) / 100
        ) * np.sqrt(252)

        forecasts.loc[date] = (
            annualized_volatility
        )

        # -------------------------------------------------
        # If a fresh model was fitted, initialize the
        # current variance for the next prediction date.
        # -------------------------------------------------

        if i % refit_frequency == 0:

            variance = float(
                variance_forecast[0]
            )

    return forecasts