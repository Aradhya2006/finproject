import pytest

from src.input.portfolio_factory import create_portfolio


def test_manual_factory():

    holdings = {
        "TCS": 10,
        "INFY": 15,
        "RELIANCE": 5,
    }

    portfolio = create_portfolio(
        "manual",
        holdings,
    )

    assert portfolio.source == "manual"

    assert portfolio.assets == [
        "TCS",
        "INFY",
        "RELIANCE",
    ]


def test_value_factory():

    values = {
        "TCS": 50000,
        "INFY": 35000,
        "RELIANCE": 20000,
    }

    portfolio = create_portfolio(
        "value",
        values,
    )

    assert portfolio.source == "value"

    assert portfolio.portfolio_value == 105000.0

    assert sum(
        portfolio.weights.values()
    ) == pytest.approx(1.0)


def test_invalid_input_type():

    with pytest.raises(ValueError):

        create_portfolio(
            "unknown",
            {},
        )


def test_input_type_case_insensitive():

    values = {
        "TCS": 50000,
        "INFY": 35000,
    }

    portfolio = create_portfolio(
        "VALUE",
        values,
    )

    assert portfolio.source == "value"