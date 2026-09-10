import numpy as np
import pytest

from src.forecasting.scaler import StandardScaler


def test_fit_transform():
    X = np.array(
        [
            [1.0, 2.0],
            [3.0, 4.0],
            [5.0, 6.0],
        ]
    )

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    assert np.isclose(X_scaled.mean(), 0.0)
    assert np.isclose(X_scaled.std(), 1.0)


def test_transform_uses_training_parameters():
    train = np.array([1.0, 2.0, 3.0])
    test = np.array([4.0, 5.0])

    scaler = StandardScaler()
    scaler.fit(train)

    transformed = scaler.transform(test)

    expected = (test - train.mean()) / train.std()

    assert np.allclose(transformed, expected)


def test_transform_before_fit():
    scaler = StandardScaler()

    with pytest.raises(ValueError):
        scaler.transform(np.array([1.0, 2.0]))


def test_empty_data():
    scaler = StandardScaler()

    with pytest.raises(ValueError):
        scaler.fit(np.array([]))


def test_zero_variance():
    scaler = StandardScaler()

    with pytest.raises(ValueError):
        scaler.fit(np.array([1.0, 1.0, 1.0]))