import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.correlation import (
    calculate_correlation_matrix,
)

from src.risk.dynamic_asset_risk import (
    calculate_dynamic_asset_volatilities,
)

from src.risk.dynamic_risk import (
    calculate_dynamic_covariance,
    calculate_dynamic_portfolio_volatility,
)


def test_real_dynamic_risk():

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
    # 1. Load actual Portfolio A data
    # -----------------------------------------

    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    asset_returns = asset_returns.set_index(
        "DATE"
    )

    # -----------------------------------------
    # 2. Calculate historical correlations
    # -----------------------------------------

    correlation_matrix = (
        calculate_correlation_matrix(
            asset_returns.reset_index()
        )
    )

    # -----------------------------------------
    # 3. Calculate current asset volatilities
    # -----------------------------------------

    forecast_volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_returns
        )
    )

    # -----------------------------------------
    # 4. Build dynamic covariance matrix
    # -----------------------------------------

    dynamic_covariance = (
        calculate_dynamic_covariance(
            forecast_volatilities,
            correlation_matrix,
        )
    )

    # -----------------------------------------
    # 5. Calculate dynamic portfolio volatility
    # -----------------------------------------

    dynamic_volatility = (
        calculate_dynamic_portfolio_volatility(
            weights,
            forecast_volatilities,
            correlation_matrix,
        )
    )

    print()
    print("REAL DYNAMIC PORTFOLIO RISK")
    print("=" * 60)

    print("\nAsset Volatilities:")

    for asset, volatility in (
        forecast_volatilities.items()
    ):
        print(
            f"{asset}: "
            f"{volatility:.4%}"
        )

    print(
        "\nDynamic Portfolio Volatility: "
        f"{dynamic_volatility:.4%}"
    )

    print("\nDynamic Covariance Matrix:")
    print(dynamic_covariance)

    assert np.isfinite(
        dynamic_volatility
    )

    assert dynamic_volatility > 0

    assert dynamic_covariance.shape == (
        5,
        5,
    )