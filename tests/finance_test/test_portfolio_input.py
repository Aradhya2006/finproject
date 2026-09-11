from src.input.portfolio_input import (
    PortfolioInput,
)


def test_portfolio_input():

    portfolio = PortfolioInput(
        holdings={
            "TCS": 10.0,
            "INFY": 15.0,
        },
        prices={
            "TCS": 2304.0,
            "INFY": 1130.0,
        },
        holding_values={
            "TCS": 23040.0,
            "INFY": 16950.0,
        },
        portfolio_value=39990.0,
        weights={
            "TCS": 23040 / 39990,
            "INFY": 16950 / 39990,
        },
        assets=[
            "TCS",
            "INFY",
        ],
        source="manual",
    )

    data = portfolio.to_dict()

    assert data["holdings"]["TCS"] == 10.0
    assert data["prices"]["INFY"] == 1130.0
    assert data["portfolio_value"] == 39990.0
    assert data["source"] == "manual"