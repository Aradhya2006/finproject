import numpy as np

from src.risk.monte_carlo import (
    calculate_cumulative_returns,
)


def test_cumulative_returns():

    simulated_returns = np.array(
        [
            [0.01, 0.02, -0.01],
            [-0.02, 0.01, 0.03],
            [0.00, 0.00, 0.00],
        ]
    )

    cumulative_returns = (
        calculate_cumulative_returns(
            simulated_returns
        )
    )

    expected = np.array(
        [
            (1.01 * 1.02 * 0.99) - 1,
            (0.98 * 1.01 * 1.03) - 1,
            0.0,
        ]
    )

    print()
    print("CUMULATIVE MONTE CARLO OUTCOMES")
    print("=" * 60)

    for value in cumulative_returns:
        print(f"{value:.6%}")

    assert cumulative_returns.shape == (3,)

    assert np.allclose(
        cumulative_returns,
        expected,
    )