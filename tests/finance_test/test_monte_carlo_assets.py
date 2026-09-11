import numpy as np
import pandas as pd

from src.risk.monte_carlo import (
    simulate_asset_returns,
)


def test_simulate_asset_returns():

    volatilities = pd.Series({
        "TCS": 0.30,
        "INFY": 0.28,
        "RELIANCE": 0.20,
    })

    correlation = pd.DataFrame(
        [
            [1.00, 0.40, 0.15],
            [0.40, 1.00, 0.20],
            [0.15, 0.20, 1.00],
        ],
        index=volatilities.index,
        columns=volatilities.index,
    )

    simulated = simulate_asset_returns(
        volatilities,
        correlation,
        simulations=1000,
        horizon=21,
        seed=42,
    )

    print()
    print("ASSET MONTE CARLO TEST")
    print("=" * 60)
    print("Shape:", simulated.shape)

    assert simulated.shape == (
        1000,
        21,
        3,
    )

    assert np.all(
        np.isfinite(simulated)
    )