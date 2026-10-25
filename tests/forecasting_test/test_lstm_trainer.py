import numpy as np
import torch

from src.forecasting.lstm_model import LSTMVolatilityModel
from src.forecasting.trainer import train_lstm


def test_training_returns_model_and_history():
    X_train = np.random.randn(32, 60).astype(np.float32)
    y_train = np.random.rand(32).astype(np.float32)

    X_validation = np.random.randn(8, 60).astype(np.float32)
    y_validation = np.random.rand(8).astype(np.float32)

    model = LSTMVolatilityModel()

    trained_model, history = train_lstm(
        model,
        X_train,
        y_train,
        X_validation,
        y_validation,
        epochs=3,
    )

    assert isinstance(trained_model, LSTMVolatilityModel)

    assert "train_loss" in history
    assert "validation_loss" in history

    assert len(history["train_loss"]) == 3
    assert len(history["validation_loss"]) == 3


def test_training_produces_finite_loss():
    X_train = np.random.randn(16, 60).astype(np.float32)
    y_train = np.random.rand(16).astype(np.float32)

    X_validation = np.random.randn(4, 60).astype(np.float32)
    y_validation = np.random.rand(4).astype(np.float32)

    model = LSTMVolatilityModel()

    _, history = train_lstm(
        model,
        X_train,
        y_train,
        X_validation,
        y_validation,
        epochs=2,
    )

    assert all(
        np.isfinite(loss)
        for loss in history["train_loss"]
    )

    assert all(
        np.isfinite(loss)
        for loss in history["validation_loss"]
    )


def test_training_updates_model_parameters():
    X_train = np.random.randn(16, 60).astype(np.float32)
    y_train = np.random.rand(16).astype(np.float32)

    X_validation = np.random.randn(4, 60).astype(np.float32)
    y_validation = np.random.rand(4).astype(np.float32)

    model = LSTMVolatilityModel()

    initial_parameters = [
        parameter.detach().clone()
        for parameter in model.parameters()
    ]

    train_lstm(
        model,
        X_train,
        y_train,
        X_validation,
        y_validation,
        epochs=2,
    )

    parameters_changed = any(
        not torch.equal(initial, updated)
        for initial, updated in zip(
            initial_parameters,
            model.parameters(),
        )
    )

    assert parameters_changed