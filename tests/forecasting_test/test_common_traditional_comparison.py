import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import (
    calculate_portfolio_returns,
)
from src.forecasting.comparison import (
    compare_volatility_forecasts,
)


def test_common_traditional_comparison():

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

    # -----------------------------------------
    # Portfolio A
    # -----------------------------------------

    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    portfolio_returns = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    portfolio_returns = (
        portfolio_returns
        .set_index("DATE")[
            "PORTFOLIO RETURN"
        ]
        .dropna()
    )

    # -----------------------------------------
    # Common test period
    # -----------------------------------------

    comparison, results = (
        compare_volatility_forecasts(
            portfolio_returns,
            evaluation_start="2024-11-27",
            evaluation_end="2026-08-06",
            rolling_window=21,
            ewma_lambda=0.94,
            realized_horizon=21,
        )
    )

    print(
        "\nCOMMON TRADITIONAL MODEL "
        "COMPARISON"
    )
    print("=" * 60)

    for model_name, metrics in results.items():

        print(
            f"\n{model_name}"
        )

        print(
            "Observations:",
            metrics["OBS"],
        )

        print(
            "MAE:",
            f"{metrics['MAE']:.6f}",
        )

        print(
            "RMSE:",
            f"{metrics['RMSE']:.6f}",
        )

        print(
            "Correlation:",
            f"{metrics['CORR']:.6f}",
        )

        print(
            "Average forecast:",
            f"{metrics['AVG FORECAST']:.6f}",
        )

        print(
            "Average realized:",
            f"{metrics['AVG REALIZED']:.6f}",
        )

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    assert len(comparison) > 0

    assert set(
        ["REALIZED", "ROLLING", "EWMA"]
    ).issubset(
        comparison.columns
    )

    for metrics in results.values():

        assert metrics["OBS"] > 0

        assert np.isfinite(
            metrics["MAE"]
        )

        assert np.isfinite(
            metrics["RMSE"]
        )

        assert np.isfinite(
            metrics["AVG FORECAST"]
        )

        assert np.isfinite(
            metrics["AVG REALIZED"]
        )

    print(
        "\nCommon traditional comparison "
        "successful"
    )