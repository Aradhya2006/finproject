import pandas as pd

from src.finance.dataset import (
    create_price_dataset,
    calculate_asset_returns,
)

from src.finance.portfolio import (
    calculate_portfolio_returns,
)

from src.forecasting.ewma import (
    calculate_ewma_volatility,
    calculate_annualized_ewma_volatility,
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

    print("Price Dataset")
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
    # EWMA volatility
    # --------------------------------------------------

    daily_ewma = calculate_ewma_volatility(
        portfolio_returns,
        lambda_=0.94,
    )

    annualized_ewma = (
        calculate_annualized_ewma_volatility(
            portfolio_returns,
            lambda_=0.94,
        )
    )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    print("\nEWMA Volatility")
    print("-" * 60)

    print(
        f"Latest daily EWMA volatility: "
        f"{daily_ewma.iloc[-1]:.6f}"
    )

    print(
        f"Latest annualized EWMA volatility: "
        f"{annualized_ewma.iloc[-1]:.4%}"
    )

    print(
        f"Average annualized EWMA volatility: "
        f"{annualized_ewma.mean():.4%}"
    )

    print(
        f"Minimum annualized EWMA volatility: "
        f"{annualized_ewma.min():.4%}"
    )

    print(
        f"Maximum annualized EWMA volatility: "
        f"{annualized_ewma.max():.4%}"
    )

    # --------------------------------------------------
    # Basic validation
    # --------------------------------------------------

    assert len(daily_ewma) == len(portfolio_returns)

    assert len(annualized_ewma) == len(
        portfolio_returns
    )

    assert daily_ewma.notna().all()

    assert annualized_ewma.notna().all()

    assert (daily_ewma >= 0).all()

    assert (annualized_ewma >= 0).all()


if __name__ == "__main__":
    main()
    