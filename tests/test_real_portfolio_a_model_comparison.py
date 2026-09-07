import pandas as pd

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import calculate_portfolio_returns

from src.forecasting.rolling import (
    calculate_rolling_volatility_forecast,
)

from src.forecasting.ewma import (
    calculate_annualized_ewma_volatility,
)

from src.forecasting.garch import (
    fit_garch,
    calculate_annualized_garch_volatility,
)

from src.forecasting.evaluation import (
    calculate_forward_realized_volatility,
    calculate_mae,
    calculate_rmse,
    calculate_forecast_correlation,
    create_volatility_forecast_dataset,
)


def test_real_portfolio_a_model_comparison():

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

    returns = portfolio_returns["PORTFOLIO RETURN"]

    # --------------------------------------------------
    # 2. Future realized volatility
    # --------------------------------------------------

    realized_volatility = calculate_forward_realized_volatility(
        returns,
        horizon=21,
    )

    # --------------------------------------------------
    # 3. Rolling volatility
    # --------------------------------------------------

    rolling_volatility = calculate_rolling_volatility_forecast(
        returns,
        window=21,
    )

    # --------------------------------------------------
    # 4. EWMA volatility
    # --------------------------------------------------

    ewma_volatility = calculate_annualized_ewma_volatility(
        returns,
        lambda_=0.94,
    )

    # --------------------------------------------------
    # 5. GARCH(1,1)
    # --------------------------------------------------

    garch_result = fit_garch(
        returns,
        p=1,
        q=1,
    )

    garch_volatility = calculate_annualized_garch_volatility(
        garch_result,
    )

    # --------------------------------------------------
    # 6. Evaluate each model
    # --------------------------------------------------

    models = {
        "Rolling": rolling_volatility,
        "EWMA": ewma_volatility,
        "GARCH": garch_volatility,
    }

    results = []

    for model_name, forecast in models.items():

        dataset = create_volatility_forecast_dataset(
            forecast,
            realized_volatility,
        )

        mae = calculate_mae(
            dataset["REALIZED"],
            dataset["FORECAST"],
        )

        rmse = calculate_rmse(
            dataset["REALIZED"],
            dataset["FORECAST"],
        )

        correlation = calculate_forecast_correlation(
            dataset["REALIZED"],
            dataset["FORECAST"],
        )

        results.append({
            "MODEL": model_name,
            "OBSERVATIONS": len(dataset),
            "MAE": mae,
            "RMSE": rmse,
            "CORRELATION": correlation,
            "AVERAGE FORECAST": dataset["FORECAST"].mean(),
            "AVERAGE REALIZED": dataset["REALIZED"].mean(),
        })

    comparison = pd.DataFrame(results)

    # --------------------------------------------------
    # 7. Display results
    # --------------------------------------------------

    print("\n" + "=" * 75)
    print("PORTFOLIO A — VOLATILITY MODEL COMPARISON")
    print("=" * 75)

    print(
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        )
    )

    print("=" * 75)

    # --------------------------------------------------
    # 8. Basic validation
    # --------------------------------------------------

    assert len(comparison) == 3

    assert comparison["MAE"].notna().all()
    assert comparison["RMSE"].notna().all()
    assert comparison["CORRELATION"].notna().all()

    assert (comparison["MAE"] >= 0).all()
    assert (comparison["RMSE"] >= 0).all()