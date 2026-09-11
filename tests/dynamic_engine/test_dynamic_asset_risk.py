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

    asset_returns = asset_returns.set_index(
        "DATE"
    )

    volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_returns
        )
    )

    print()
    print("DYNAMIC ASSET VOLATILITY")
    print("=" * 60)

    for asset, volatility in volatilities.items():
        print(
            f"{asset}: "
            f"{volatility:.4%}"
        )

    assert len(volatilities) == 5

    assert np.all(
        np.isfinite(
            volatilities.to_numpy()
        )
    )

    assert np.all(
        volatilities.to_numpy() > 0
    )

    assert list(
        volatilities.index
    ) == symbols