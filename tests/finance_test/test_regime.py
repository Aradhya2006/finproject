import numpy as np
import pandas as pd

from src.risk.regime import (
    calculate_rolling_volatility,
    classify_volatility_regimes,
)


def test_calculate_rolling_volatility():

    returns = pd.Series(
        [0.01, -0.02, 0.015, -0.01, 0.005, 0.02]
    )

    volatility = calculate_rolling_volatility(
        returns,
        window=3,
    )

    # First two observations cannot have
    # a 3-day rolling standard deviation.
    assert volatility.iloc[:2].isna().all()

    # Remaining observations should contain values.
    assert volatility.iloc[2:].notna().all()

    # Volatility cannot be negative.
    assert (volatility.dropna() >= 0).all()


def test_calculate_rolling_volatility_invalid_window():

    returns = pd.Series(
        [0.01, -0.02, 0.015]
    )

    try:
        calculate_rolling_volatility(
            returns,
            window=1,
        )
        assert False
    except ValueError:
        assert True


def test_classify_volatility_regimes():

    volatility = pd.Series(
        np.arange(1, 31, dtype=float)
    )

    regimes = classify_volatility_regimes(
        volatility
    )

    # Every observation should receive a regime.
    assert len(regimes) == len(volatility)

    assert regimes.notna().all()

    # Only the three expected regimes are allowed.
    assert set(regimes.unique()) == {
        "LOW",
        "NORMAL",
        "HIGH",
    }

    # Each regime should contain observations.
    assert (regimes == "LOW").sum() > 0
    assert (regimes == "NORMAL").sum() > 0
    assert (regimes == "HIGH").sum() > 0


def test_classify_volatility_regimes_too_few_observations():

    volatility = pd.Series([0.1, 0.2])

    try:
        classify_volatility_regimes(volatility)
        assert False
    except ValueError:
        assert True