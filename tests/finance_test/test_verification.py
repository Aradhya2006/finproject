import pytest

from src.input.verification import (
    verify_holdings,
)


def test_confirm_detected_holdings():

    detected = {
        "TCS": 10.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }

    verified = verify_holdings(
        detected
    )

    assert verified == detected


def test_user_edits_detected_holdings():

    detected = {
        "TCS": 10.0,
        "INFY": 15.0,
    }

    confirmed = {
        "TCS": 20.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }

    verified = verify_holdings(
        detected,
        confirmed,
    )

    assert verified == confirmed


def test_empty_detected_holdings():

    with pytest.raises(ValueError):

        verify_holdings({})


def test_invalid_detected_holdings():

    with pytest.raises(ValueError):

        verify_holdings(
            ["TCS", 10]
        )


def test_empty_confirmed_holdings():

    detected = {
        "TCS": 10.0,
    }

    with pytest.raises(ValueError):

        verify_holdings(
            detected,
            {},
        )