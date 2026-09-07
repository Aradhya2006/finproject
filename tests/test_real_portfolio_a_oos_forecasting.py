import numpy as np
import pandas as pd

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import calculate_portfolio_returns

from src.forecasting.ewma import (
    calculate_ewma_variance,
)

from src.forecasting.garch import (
    fit_garch,
    forecast_garch_volatility,
)

from src.forecasting.evaluation import (
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
)


def test_real_portfolio_a_oos_forecasting():

    # --------------------------------------------------
    # 1. Portfolio A
    # --------------------------------------------------

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

    price_data = create_price_dataset(symbols)

    asset_returns = calculate_asset_returns(price_data)

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    returns = portfolio_returns["PORTFOLIO RETURN"].dropna()

    # --------------------------------------------------
    # 2. Settings
    # --------------------------------------------------

    horizon = 21
    refit_frequency = 21
    minimum_training_size = 1000

    evaluation_start = max(
        minimum_training_size,
        len(returns) - 504,
    )

    forecast_dates = []
    rolling_forecasts = []
    ewma_forecasts = []
    garch_forecasts = []
    realized_values = []

    # --------------------------------------------------
    # 3. Initial GARCH fit
    # --------------------------------------------------

    garch_result = fit_garch(
        returns.iloc[:evaluation_start],
        p=1,
        q=1,
    )

    # --------------------------------------------------
    # 4. Daily OOS forecasts
    # --------------------------------------------------

    for i in range(
        evaluation_start,
        len(returns) - horizon,
    ):

        # Refit only every 21 trading days.
        if (i - evaluation_start) % refit_frequency == 0:

            train_returns = returns.iloc[:i]

            garch_result = fit_garch(
                train_returns,
                p=1,
                q=1,
            )

        train_returns = returns.iloc[:i]

        current_date = returns.index[i]

        # ----------------------------------------------
        # Rolling forecast
        # ----------------------------------------------

        rolling_forecast = (
            train_returns
            .iloc[-21:]
            .std(ddof=1)
            * np.sqrt(252)
        )

        # ----------------------------------------------
        # EWMA forecast
        # ----------------------------------------------

        ewma_variance = calculate_ewma_variance(
            train_returns,
            lambda_=0.94,
        )

        ewma_forecast = (
            np.sqrt(ewma_variance.iloc[-1])
            * np.sqrt(252)
        )

        # ----------------------------------------------
        # GARCH forecast
        # ----------------------------------------------

        garch_forecast = forecast_garch_volatility(
            garch_result,
            horizon=1,
        )

        garch_forecast = (
            garch_forecast.iloc[0]
            * np.sqrt(252)
        )

        # ----------------------------------------------
        # Future realized volatility
        # ----------------------------------------------

        future_returns = returns.iloc[
            i + 1:i + 1 + horizon
        ]

        realized = (
            future_returns.std(ddof=1)
            * np.sqrt(252)
        )

        forecast_dates.append(current_date)
        rolling_forecasts.append(rolling_forecast)
        ewma_forecasts.append(ewma_forecast)
        garch_forecasts.append(garch_forecast)
        realized_values.append(realized)

    # --------------------------------------------------
    # 5. Evaluation dataset
    # --------------------------------------------------

    evaluation = pd.DataFrame({
        "DATE": forecast_dates,
        "REALIZED": realized_values,
        "ROLLING": rolling_forecasts,
        "EWMA": ewma_forecasts,
        "GARCH": garch_forecasts,
    })

    evaluation = evaluation.set_index("DATE")

    # --------------------------------------------------
    # 6. Model comparison
    # --------------------------------------------------

    models = [
        "ROLLING",
        "EWMA",
        "GARCH",
    ]

    results = []

    for model in models:

        mae = calculate_mae(
            evaluation["REALIZED"],
            evaluation[model],
        )

        rmse = calculate_rmse(
            evaluation["REALIZED"],
            evaluation[model],
        )

        correlation = calculate_forecast_correlation(
            evaluation["REALIZED"],
            evaluation[model],
        )

        results.append({
            "MODEL": model,
            "OBSERVATIONS": len(evaluation),
            "MAE": mae,
            "RMSE": rmse,
            "CORRELATION": correlation,
            "AVERAGE FORECAST": evaluation[model].mean(),
            "AVERAGE REALIZED": evaluation["REALIZED"].mean(),
        })

    comparison = pd.DataFrame(results)

    # --------------------------------------------------
    # 7. Display
    # --------------------------------------------------

    print("\n" + "=" * 90)
    print("PORTFOLIO A — ROBUST OUT-OF-SAMPLE VOLATILITY FORECASTING")
    print("=" * 90)

    print(f"\nEvaluation start: {evaluation.index[0]}")
    print(f"Evaluation end:   {evaluation.index[-1]}")

    print(f"\nForecast observations: {len(evaluation)}")
    print(f"Forecast horizon:      {horizon} trading days")
    print(f"GARCH refit frequency: {refit_frequency} trading days")

    print("\nMODEL COMPARISON")

    print(
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        )
    )

    print("=" * 90)

    # --------------------------------------------------
    # 8. Validation
    # --------------------------------------------------

    assert len(evaluation) > 100
    assert len(comparison) == 3

    assert comparison["MAE"].notna().all()
    assert comparison["RMSE"].notna().all()
    assert comparison["CORRELATION"].notna().all()

    assert (comparison["MAE"] >= 0).all()
    assert (comparison["RMSE"] >= 0).all()