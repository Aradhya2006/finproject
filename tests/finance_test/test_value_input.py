import pytest

from src.input.value_input import (
    validate_portfolio_values,
    create_value_portfolio,
)


def test_validate_portfolio_values():

    values = {
        "tcs": 50000,
        "INFY": 35000,
        "reliance": 20000,
    }

    result = validate_portfolio_values(values)

    assert result == {
        "TCS": 50000.0,
        "INFY": 35000.0,
        "RELIANCE": 20000.0,
    }


def test_create_value_portfolio():

    values = {
        "TCS": 50000,
        "INFY": 35000,
        "RELIANCE": 20000,
    }

    portfolio = create_value_portfolio(values)

    assert portfolio.portfolio_value == 105000.0

    assert portfolio.holding_values == {
        "TCS": 50000.0,
        "INFY": 35000.0,
        "RELIANCE": 20000.0,
    }

    assert portfolio.weights["TCS"] == pytest.approx(
        50000 / 105000
    )

    assert portfolio.weights["INFY"] == pytest.approx(
        35000 / 105000
    )

    assert portfolio.weights["RELIANCE"] == pytest.approx(
        20000 / 105000
    )

    assert sum(portfolio.weights.values()) == pytest.approx(
        1.0
    )

    assert portfolio.source == "value"


def test_empty_values():

    with pytest.raises(ValueError):
        validate_portfolio_values({})


def test_negative_value():

    with pytest.raises(ValueError):
        validate_portfolio_values({
            "TCS": -50000
        })


def test_zero_value():

    with pytest.raises(ValueError):
        validate_portfolio_values({
            "TCS": 0
        })


def test_invalid_value():

    with pytest.raises(ValueError):
        validate_portfolio_values({
            "TCS": "abc"
        })


def test_non_dictionary():

    with pytest.raises(ValueError):
        validate_portfolio_values([
            ("TCS", 50000)
        ])