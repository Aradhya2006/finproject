import numpy as np

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.risk.dynamic_asset_risk import (
    calculate_dynamic_asset_volatilities,
)


def test_dynamic_asset_risk():

    symbols = [
        "TCS",
        "INFY",
        "HCLTECH",
        "WIPRO",
        "RELIANCE",
    ]

    price_data = create_price_dataset(
        symbols
    )

    asset_returns = calculate_asset_returns(
        price_data
    )

    asset_returns = (
        asset_returns
        .set_index("DATE")
        [symbols]
    )

    dynamic_volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_returns,
            lambda_=0.94,
        )
    )

    print()
    print("DYNAMIC ASSET VOLATILITIES")
    print("=" * 60)

    for asset, volatility in (
        dynamic_volatilities.items()
    ):
        print(
            f"{asset:<12} "
            f"{volatility:.4%}"
        )

    print()

    assert len(dynamic_volatilities) == len(
        symbols
    )

    assert list(
        dynamic_volatilities.index
    ) == symbols

    assert np.all(
        np.isfinite(
            dynamic_volatilities.to_numpy()
        )
    )

    assert np.all(
        dynamic_volatilities.to_numpy() > 0
    )