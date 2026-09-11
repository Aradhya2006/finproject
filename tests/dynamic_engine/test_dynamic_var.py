import numpy as np

from src.risk.dynamic_var import (
    calculate_dynamic_parametric_var,
)


def test_dynamic_var():

    portfolio_volatility = 0.178310

    portfolio_value = 1_000_000

    var = calculate_dynamic_parametric_var(
        portfolio_volatility,
        confidence_level=0.95,
        portfolio_value=portfolio_value,
    )

    print()
    print("DYNAMIC PARAMETRIC VAR")
    print("=" * 60)

    print(
        f"Portfolio volatility: "
        f"{portfolio_volatility:.4%}"
    )

    print(
        f"Portfolio value: "
        f"₹{portfolio_value:,.2f}"
    )

    print(
        f"95% one-day VaR: "
        f"₹{var:,.2f}"
    )

    assert np.isfinite(var)

    assert var > 0