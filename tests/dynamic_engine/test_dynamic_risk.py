import numpy as np
import pandas as pd

from src.risk.dynamic_risk import (
    calculate_dynamic_covariance,
    calculate_dynamic_portfolio_volatility,
)


def test_dynamic_risk():

    assets = [
        "A",
        "B",
        "C",
    ]

    forecast_volatilities = pd.Series(
        {
            "A": 0.20,
            "B": 0.25,
            "C": 0.30,
        }
    )

    correlation_matrix = pd.DataFrame(
        [
            [1.00, 0.40, 0.20],
            [0.40, 1.00, 0.30],
            [0.20, 0.30, 1.00],
        ],
        index=assets,
        columns=assets,
    )

    weights = {
        "A": 0.40,
        "B": 0.35,
        "C": 0.25,
    }

    covariance = calculate_dynamic_covariance(
        forecast_volatilities,
        correlation_matrix,
    )

    assert covariance.shape == (3, 3)

    assert np.allclose(
        np.diag(covariance),
        forecast_volatilities.to_numpy() ** 2,
    )

    portfolio_volatility = (
        calculate_dynamic_portfolio_volatility(
            weights,
            forecast_volatilities,
            correlation_matrix,
        )
    )

    assert np.isfinite(portfolio_volatility)

    assert portfolio_volatility > 0

    print()
    print("DYNAMIC RISK TEST")
    print("=" * 60)
    print("Portfolio volatility:", portfolio_volatility)