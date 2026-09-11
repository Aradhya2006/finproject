import pytest
from src.input.manual import (
    create_current_manual_portfolio,
)
from src.input.manual import (
    validate_holdings,
    create_manual_portfolio,
)


def test_validate_holdings():

    holdings = {
        "tcs": 10,
        "INFY": 15,
        " reliance ": 5,
    }

    validated = validate_holdings(
        holdings
    )

    print()
    print("MANUAL PORTFOLIO INPUT TEST")
    print("=" * 60)
    print("Validated holdings:")
    print(validated)

    assert validated == {
        "TCS": 10.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }


def test_create_manual_portfolio():

    portfolio = create_manual_portfolio(
        {
            "TCS": 10,
            "INFY": 15,
        }
    )

    assert portfolio == {
        "holdings": {
            "TCS": 10.0,
            "INFY": 15.0,
        },
        "assets": [
            "TCS",
            "INFY",
        ],
    }


def test_empty_holdings():

    with pytest.raises(ValueError):
        validate_holdings({})


def test_negative_quantity():

    with pytest.raises(ValueError):
        validate_holdings({
            "TCS": -5,
        })


def test_invalid_quantity():

    with pytest.raises(ValueError):
        validate_holdings({
            "TCS": "ten",
        })
        
        
        
def test_calculate_portfolio_from_holdings():

    from src.input.manual import (
        calculate_portfolio_from_holdings,
    )

    holdings = {
        "TCS": 10,
        "INFY": 15,
        "RELIANCE": 5,
    }

    prices = {
        "TCS": 3500,
        "INFY": 1500,
        "RELIANCE": 1400,
    }

    portfolio = (
        calculate_portfolio_from_holdings(
            holdings,
            prices,
        )
    )

    print()
    print("PORTFOLIO VALUATION TEST")
    print("=" * 60)
    print(
        "Holding values:",
        portfolio["holding_values"],
    )
    print(
        "Portfolio value:",
        portfolio["portfolio_value"],
    )
    print(
        "Weights:",
        portfolio["weights"],
    )

    assert portfolio["holding_values"] == {
        "TCS": 35000.0,
        "INFY": 22500.0,
        "RELIANCE": 7000.0,
    }

    assert (
        portfolio["portfolio_value"]
        == 64500.0
    )

    assert abs(
        sum(
            portfolio["weights"].values()
        ) - 1.0
    ) < 1e-10
    
    
    
def test_missing_price():

    from src.input.manual import (
        calculate_portfolio_from_holdings,
    )

    with pytest.raises(ValueError):
        calculate_portfolio_from_holdings(
            {"TCS": 10},
            {},
        )


def test_invalid_price():

    from src.input.manual import (
        calculate_portfolio_from_holdings,
    )

    with pytest.raises(ValueError):
        calculate_portfolio_from_holdings(
            {"TCS": 10},
            {"TCS": -100},
        )
        
        
        
        
def test_create_current_manual_portfolio():

    holdings = {
        "TCS": 10,
        "INFY": 15,
        "RELIANCE": 5,
    }

    portfolio = create_current_manual_portfolio(
        holdings
    )

    print()
    print("CURRENT MANUAL PORTFOLIO TEST")
    print("=" * 60)

    print(
        "Prices:",
        portfolio["prices"]
    )

    print(
        "Holding values:",
        portfolio["holding_values"]
    )

    print(
        "Portfolio value:",
        portfolio["portfolio_value"]
    )

    print(
        "Weights:",
        portfolio["weights"]
    )

    assert set(
        portfolio["assets"]
    ) == set(holdings.keys())

    assert portfolio["portfolio_value"] > 0

    assert abs(
        sum(portfolio["weights"].values()) - 1.0
    ) < 1e-10