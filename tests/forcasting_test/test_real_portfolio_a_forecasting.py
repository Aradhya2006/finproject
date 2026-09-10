import pandas as pd

from src.forecasting.evaluation import (
    calculate_forward_realized_volatility,
    calculate_mae,
    calculate_rmse,
    create_volatility_forecast_dataset,
    calculate_forecast_correlation,
)
from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import (
    calculate_portfolio_returns,
)

from src.forecasting.ewma import (
    calculate_annualized_ewma_volatility,
)

from src.forecasting.evaluation import (
    calculate_forward_realized_volatility,
    calculate_mae,
    calculate_rmse,
)


def main():

    # --------------------------------------------------
    # Portfolio A
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

    # --------------------------------------------------
    # Load data
    # --------------------------------------------------

    price_data = create_price_dataset(symbols)

    print("Portfolio A Forecasting Evaluation")
    print("-" * 60)

    print(f"Start: {price_data['DATE'].min()}")
    print(f"End:   {price_data['DATE'].max()}")
    print(f"Rows:  {len(price_data)}")

    # --------------------------------------------------
    # Asset returns
    # --------------------------------------------------

    asset_returns = calculate_asset_returns(
        price_data
    )

    # --------------------------------------------------
    # Portfolio returns
    # --------------------------------------------------

    portfolio_data = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    portfolio_returns = pd.Series(
        portfolio_data["PORTFOLIO RETURN"].values,
        index=portfolio_data["DATE"],
    )

    # --------------------------------------------------
    # EWMA volatility estimate
    # --------------------------------------------------

    ewma_volatility = (
        calculate_annualized_ewma_volatility(
            portfolio_returns,
            lambda_=0.94,
        )
    )

    # --------------------------------------------------
    # Forward realized volatility
    # --------------------------------------------------

    realized_volatility = (
        calculate_forward_realized_volatility(
            portfolio_returns,
            horizon=21,
        )
        * 1.0
    )

    # --------------------------------------------------
    # Align forecast and realized volatility
    # --------------------------------------------------

    evaluation_data = create_volatility_forecast_dataset(
    ewma_volatility,
    realized_volatility,
)

    # --------------------------------------------------
    # Forecast metrics
    # --------------------------------------------------

    mae = calculate_mae(
        evaluation_data["REALIZED"],
        evaluation_data["EWMA"],
    )

    rmse = calculate_rmse(
        evaluation_data["REALIZED"],
        evaluation_data["EWMA"],
    )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    print("\nEWMA Forecast Evaluation")
    print("-" * 60)

    print(
        f"Evaluation observations: "
        f"{len(evaluation_data)}"
    )

    print(
        f"MAE:  {mae:.6f}"
    )

    print(
        f"RMSE: {rmse:.6f}"
    )

    print("\nAverage Volatility")
    print("-" * 60)

    print(
        f"Average EWMA volatility: "
        f"{evaluation_data['EWMA'].mean():.4%}"
    )

    print(
        f"Average realized volatility: "
        f"{evaluation_data['REALIZED'].mean():.4%}"
    )

    mae = calculate_mae(
    evaluation_data["REALIZED"],
    evaluation_data["FORECAST"],
)

    rmse = calculate_rmse(
    evaluation_data["REALIZED"],
    evaluation_data["FORECAST"],
)

    correlation = calculate_forecast_correlation(
    evaluation_data["REALIZED"],
    evaluation_data["FORECAST"],
)

    print(
    f"MAE:  {mae:.6f}"
)

    print(
    f"RMSE: {rmse:.6f}"
)

    print(
    f"Correlation: {correlation:.6f}"
)
    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    assert len(evaluation_data) > 0

    assert mae >= 0

    assert rmse >= 0

    assert evaluation_data["FORECAST"].notna().all()

    assert evaluation_data["REALIZED"].notna().all()


if __name__ == "__main__":
    main()