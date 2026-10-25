import numpy as np
import pandas as pd
import pytest

from src.forecasting.split import chronological_split


def create_test_data():
    X = np.arange(1000).reshape(100, 10)
    y = np.arange(100, dtype=float)
    dates = pd.date_range(
        "2020-01-01",
        periods=100,
        freq="D",
    )

    return X, y, dates


def test_chronological_split():
    X, y, dates = create_test_data()

    result = chronological_split(
        X,
        y,
        dates,
        train_ratio=0.70,
        validation_ratio=0.15,
    )

    (
        X_train,
        y_train,
        dates_train,
        X_validation,
        y_validation,
        dates_validation,
        X_test,
        y_test,
        dates_test,
    ) = result

    assert len(X_train) == 70
    assert len(X_validation) == 15
    assert len(X_test) == 15

    assert len(y_train) == 70
    assert len(y_validation) == 15
    assert len(y_test) == 15


def test_split_is_chronological():
    X, y, dates = create_test_data()

    result = chronological_split(X, y, dates)

    (
        _,
        _,
        dates_train,
        _,
        _,
        dates_validation,
        _,
        _,
        dates_test,
    ) = result

    assert dates_train[-1] < dates_validation[0]
    assert dates_validation[-1] < dates_test[0]


def test_data_is_not_shuffled():
    X, y, dates = create_test_data()

    result = chronological_split(X, y, dates)

    X_train = result[0]
    X_test = result[6]

    assert np.array_equal(X_train[0], X[0])
    assert np.array_equal(X_test[0], X[85])


def test_invalid_ratios():
    X, y, dates = create_test_data()

    with pytest.raises(ValueError):
        chronological_split(
            X,
            y,
            dates,
            train_ratio=0.8,
            validation_ratio=0.3,
        )


def test_mismatched_lengths():
    X, y, dates = create_test_data()

    with pytest.raises(ValueError):
        chronological_split(
            X[:-1],
            y,
            dates,
        )