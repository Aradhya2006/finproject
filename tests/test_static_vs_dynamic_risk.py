import numpy as np
import pandas as pd

from src.finance.portfolio import (
    calculate_portfolio_returns,
)

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
    calculate_dynamic_portfolio_volatility,
)

from src.risk.parametric_var import (
    calculate_parametric_var,
)

from src.risk.dynamic_var import (
    calculate_dynamic_parametric_var,
)

from src.risk.dynamic_cvar import (
    calculate_dynamic_parametric_cvar,
)


def test_static_vs_dynamic_risk():

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

    portfolio_value = 1_000_000

    # -----------------------------------------
    # 1. Load actual Portfolio A returns
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
    # 2. Static historical covariance
    # -----------------------------------------

    correlation_matrix = (
        calculate_correlation_matrix(
            asset_returns.reset_index()
        )
    )

    covariance_matrix = (
        asset_returns.cov()
    )

    # -----------------------------------------
    # Calculate static portfolio volatility
    # explicitly using w^T Sigma w
    # -----------------------------------------

    weight_vector = np.array(
        [
            weights[asset]
            for asset in symbols
        ]
    )

    covariance = (
        covariance_matrix
        .loc[symbols, symbols]
        .to_numpy()
    )

    static_variance = (
        weight_vector.T
        @ covariance
        @ weight_vector
    )

    static_volatility = (
        np.sqrt(static_variance)
        * np.sqrt(252)
    )

    # -----------------------------------------
    # 3. Dynamic asset volatilities
    # -----------------------------------------

    dynamic_asset_volatilities = (
        calculate_dynamic_asset_volatilities(
            asset_returns
        )
    )

    dynamic_volatility = (
        calculate_dynamic_portfolio_volatility(
            weights,
            dynamic_asset_volatilities,
            correlation_matrix,
        )
    )

    # -----------------------------------------
    # 4. Static VaR
    # -----------------------------------------

    portfolio_returns = calculate_portfolio_returns(
        asset_returns.reset_index(),
        weights,
    )

    portfolio_return_series = (
        portfolio_returns
        .set_index("DATE")["PORTFOLIO RETURN"]
        .dropna()
    )

    static_var_percentage = calculate_parametric_var(
        portfolio_return_series,
        confidence_level=0.95,
    )

    static_var = (
        static_var_percentage
        * portfolio_value
    )

    # -----------------------------------------
    # 5. Dynamic VaR
    # -----------------------------------------

    dynamic_var = (
        calculate_dynamic_parametric_var(
            dynamic_volatility,
            confidence_level=0.95,
            portfolio_value=portfolio_value,
        )
    )

    # -----------------------------------------
    # 6. Dynamic CVaR
    # -----------------------------------------

    dynamic_cvar = (
        calculate_dynamic_parametric_cvar(
            dynamic_volatility,
            confidence_level=0.95,
            portfolio_value=portfolio_value,
        )
    )

    # -----------------------------------------
    # 7. Results
    # -----------------------------------------

    print()
    print("STATIC VS DYNAMIC RISK")
    print("=" * 60)

    print(
        f"Static volatility:  "
        f"{static_volatility:.4%}"
    )

    print(
        f"Dynamic volatility: "
        f"{dynamic_volatility:.4%}"
    )

    print()

    print(
        f"Static 95% VaR:     "
        f"₹{static_var:,.2f}"
    )

    print(
        f"Dynamic 95% VaR:    "
        f"₹{dynamic_var:,.2f}"
    )

    print(
        f"Dynamic 95% CVaR:   "
        f"₹{dynamic_cvar:,.2f}"
    )

    print()

    volatility_change = (
        dynamic_volatility
        / static_volatility
        - 1
    )

    var_change = (
        dynamic_var
        / static_var
        - 1
    )

    print(
        f"Volatility change:  "
        f"{volatility_change:+.2%}"
    )

    print(
        f"VaR change:         "
        f"{var_change:+.2%}"
    )

    # -----------------------------------------
    # 8. Validation
    # -----------------------------------------

    assert np.isfinite(
        static_volatility
    )

    assert np.isfinite(
        dynamic_volatility
    )

    assert static_volatility > 0
    assert dynamic_volatility > 0

    assert np.isfinite(
        static_var
    )

    assert np.isfinite(
        dynamic_var
    )

    assert np.isfinite(
        dynamic_cvar
    )

    assert static_var > 0
    assert dynamic_var > 0
    assert dynamic_cvar > dynamic_var