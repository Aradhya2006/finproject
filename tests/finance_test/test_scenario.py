from src.risk.scenario import (
    apply_portfolio_shock,
    apply_sector_shock,
    apply_broad_market_shock,
    apply_single_asset_shock,
)


def test_scenario():

    weights = {
        "TCS": 0.30,
        "HDFCBANK": 0.25,
        "RELIANCE": 0.20,
        "GOLDBEES": 0.25,
    }

    sectors = {
        "TCS": "IT",
        "HDFCBANK": "BANKING",
        "RELIANCE": "ENERGY",
        "GOLDBEES": "GOLD",
    }

    print()
    print("PORTFOLIO SCENARIO TEST")
    print("=" * 60)

    # Custom asset shock
    custom = apply_portfolio_shock(
        weights,
        {
            "TCS": -0.20,
            "HDFCBANK": -0.10,
            "RELIANCE": 0.0,
            "GOLDBEES": 0.05,
        },
    )

    print(
        f"Custom scenario: {custom:.2%}"
    )

    # Sector shock
    it_shock = apply_sector_shock(
        weights,
        sectors,
        "IT",
        -0.20,
    )

    print(
        f"IT sector shock: {it_shock:.2%}"
    )

    # Broad equity-market shock
    market_shock = apply_broad_market_shock(
        weights,
        -0.15,
        excluded_assets={"GOLDBEES"},
    )

    print(
        f"Broad market shock: "
        f"{market_shock:.2%}"
    )

    # Single asset shock
    single_shock = apply_single_asset_shock(
        weights,
        "RELIANCE",
        -0.30,
    )

    print(
        f"Reliance shock: "
        f"{single_shock:.2%}"
    )

    assert custom == (
        0.30 * -0.20
        + 0.25 * -0.10
        + 0.20 * 0.0
        + 0.25 * 0.05
    )

    assert it_shock == (
        0.30 * -0.20
    )

    assert market_shock == (
        0.30 * -0.15
        + 0.25 * -0.15
        + 0.20 * -0.15
    )

    assert single_shock == (
        0.20 * -0.30
    )