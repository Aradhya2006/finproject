import numpy as np
from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.correlation import (
    calculate_covariance_matrix,
)

from src.finance.risk_contribution import (
    calculate_marginal_risk_contribution,
    calculate_component_risk_contribution,
    calculate_percentage_risk_contribution,
)


def test_risk_contribution():

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

    prices = create_price_dataset(symbols)

    returns = calculate_asset_returns(
        prices
    )

    covariance_matrix = (
        calculate_covariance_matrix(
            returns
        )
    )

    marginal = (
        calculate_marginal_risk_contribution(
            weights,
            covariance_matrix,
        )
    )

    component = (
        calculate_component_risk_contribution(
            weights,
            covariance_matrix,
        )
    )

    percentage = (
        calculate_percentage_risk_contribution(
            weights,
            covariance_matrix,
        )
    )

    assert len(marginal) == len(symbols)
    assert len(component) == len(symbols)
    assert len(percentage) == len(symbols)

    assert all(
        value >= 0
        for value in percentage.values()
    )

    assert np.isclose(
        sum(percentage.values()),
        1.0,
    )

    print("\nRisk Contribution")
    print("-" * 40)

    for symbol in symbols:
        print(
            f"{symbol}: "
            f"{percentage[symbol] * 100:.2f}%"
        )


if __name__ == "__main__":
    test_risk_contribution()
    print("\nRisk contribution test passed!")