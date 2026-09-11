import numpy as np

from src.risk.dynamic_cvar import (
    calculate_dynamic_parametric_cvar,
)


def test_dynamic_cvar():

    portfolio_volatility = 0.178310

    portfolio_value = 1_000_000

    cvar = calculate_dynamic_parametric_cvar(
        portfolio_volatility,
        confidence_level=0.95,
        portfolio_value=portfolio_value,
    )

    print()
    print("DYNAMIC PARAMETRIC CVAR")
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
        f"95% one-day CVaR: "
        f"₹{cvar:,.2f}"
    )

    assert np.isfinite(cvar)
    assert cvar > 0