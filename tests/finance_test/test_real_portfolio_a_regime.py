import pandas as pd

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import (
    calculate_portfolio_returns,
)

from src.risk.backtesting import (
    backtest_historical_var,
)

from src.risk.regime import (
    calculate_rolling_volatility,
    classify_volatility_regimes,
)


def main():

    # --------------------------------------------------
    # Portfolio A
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Load price data
    # --------------------------------------------------

    price_data = create_price_dataset(symbols)

    print("Price dataset")
    print("-" * 60)
    print(f"Start: {price_data['DATE'].min()}")
    print(f"End:   {price_data['DATE'].max()}")
    print(f"Rows:  {len(price_data)}")

    # --------------------------------------------------
    # Calculate asset returns
    # --------------------------------------------------

    asset_returns = calculate_asset_returns(
        price_data
    )

    # --------------------------------------------------
    # Calculate portfolio returns
    # --------------------------------------------------

    portfolio_data = calculate_portfolio_returns(
        asset_returns,
        weights,
    )

    portfolio_returns = pd.Series(
        portfolio_data["PORTFOLIO RETURN"].values,
        index=portfolio_data["DATE"],
    )

    # --------------------------------------------------
    # Rolling volatility
    # --------------------------------------------------

    rolling_volatility = calculate_rolling_volatility(
        portfolio_returns,
        window=21,
    )

    # --------------------------------------------------
    # Classify regimes
    # --------------------------------------------------

    regimes = classify_volatility_regimes(
        rolling_volatility
    )

    print("\nVolatility Regimes")
    print("-" * 60)

    print(
        regimes.value_counts()
        .sort_index()
    )

    # --------------------------------------------------
    # Historical VaR Backtest
    # --------------------------------------------------

    backtest_results = backtest_historical_var(
        portfolio_returns,
        confidence_level=0.95,
        window=252,
    )

    # --------------------------------------------------
    # Align regimes with VaR backtest
    # --------------------------------------------------

    backtest_results["REGIME"] = (
        regimes.reindex(
            backtest_results["DATE"]
        ).values
    )

    backtest_results = backtest_results.dropna(
        subset=["REGIME"]
    )

    # --------------------------------------------------
    # Violation statistics by regime
    # --------------------------------------------------

    regime_summary = (
        backtest_results
        .groupby("REGIME")
        .agg(
            observations=("VIOLATION", "size"),
            violations=("VIOLATION", "sum"),
            violation_rate=("VIOLATION", "mean"),
            average_var=("VAR", "mean"),
            average_return=("ACTUAL RETURN", "mean"),
        )
        .sort_index()
    )

    print("\nVaR Performance by Volatility Regime")
    print("-" * 60)

    print(
    regime_summary.to_string(
        float_format=lambda x: f"{x:.6f}"
    )
)
    # --------------------------------------------------
    # High-volatility regime
    # --------------------------------------------------

    high_regime = backtest_results[
        backtest_results["REGIME"] == "HIGH"
    ]

    print("\nHigh Volatility Regime")
    print("-" * 60)

    print(
        f"Observations: {len(high_regime)}"
    )

    print(
        f"Violations: "
        f"{high_regime['VIOLATION'].sum()}"
    )

    print(
        f"Violation rate: "
        f"{high_regime['VIOLATION'].mean():.4f}"
    )

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    assert len(regimes) > 0

    assert set(regimes.unique()) <= {
        "LOW",
        "NORMAL",
        "HIGH",
    }

    assert len(backtest_results) > 0

    assert backtest_results["REGIME"].notna().all()

    assert (
        regime_summary["violations"].sum()
        == backtest_results["VIOLATION"].sum()
    )


if __name__ == "__main__":
    main()
