import torch
import torch.nn as nn


class LSTMVolatilityModel(nn.Module):
    def __init__(
        self,
        input_size=1,
        hidden_size=32,
        num_layers=2,
        dropout=0.2,
    ):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        output, _ = self.lstm(x)

        # Use the final time step
        last_output = output[:, -1, :]

        prediction = self.fc(last_output)

        return prediction.squeeze(-1)