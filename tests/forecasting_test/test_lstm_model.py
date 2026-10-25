import torch

from src.forecasting.lstm_model import LSTMVolatilityModel


def test_model_output_shape():
    model = LSTMVolatilityModel()

    X = torch.randn(16, 60, 1)

    output = model(X)

    assert output.shape == (16,)


def test_model_forward_pass():
    model = LSTMVolatilityModel()

    X = torch.randn(8, 60, 1)

    output = model(X)

    assert torch.isfinite(output).all()


def test_model_can_backpropagate():
    model = LSTMVolatilityModel()

    X = torch.randn(8, 60, 1)
    y = torch.randn(8)

    output = model(X)

    loss = torch.mean((output - y) ** 2)

    loss.backward()

    gradients_exist = any(
        parameter.grad is not None
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    assert gradients_exist