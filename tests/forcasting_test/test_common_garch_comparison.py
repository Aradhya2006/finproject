from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)
from src.finance.portfolio import (
    calculate_portfolio_returns,
)
from src.forecasting.garch_comparison import (
    evaluate_garch_common_period,
)


def test_common_garch_comparison():

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

    comparison, results = (
        evaluate_garch_common_period(
            portfolio_returns,
            evaluation_start="2024-11-27",
            evaluation_end="2026-08-06",
            realized_horizon=21,
            refit_frequency=21,
        )
    )

    print(
        "\nCOMMON GARCH MODEL COMPARISON"
    )
    print("=" * 60)

    print(
        "Observations:",
        results["OBS"],
    )

    print(
        "MAE:",
        f"{results['MAE']:.6f}",
    )

    print(
        "RMSE:",
        f"{results['RMSE']:.6f}",
    )

    print(
        "Correlation:",
        f"{results['CORR']:.6f}",
    )

    print(
        "Average forecast:",
        f"{results['AVG FORECAST']:.6f}",
    )

    print(
        "Average realized:",
        f"{results['AVG REALIZED']:.6f}",
    )

    assert len(comparison) == 420
    assert results["OBS"] == 420

    print(
        "\nCommon GARCH comparison successful"
    )