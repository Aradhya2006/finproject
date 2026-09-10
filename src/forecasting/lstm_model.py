import torch
import torch.nn as nn


class VolatilityLSTM(nn.Module):
    """
    LSTM model for forward volatility forecasting.
    """

    def __init__(
        self,
        input_size=5,
        hidden_size=64,
        num_layers=1,
        dropout=0.2,
    ):
        super().__init__()

        # Dropout inside LSTM only works when num_layers > 1.
        lstm_dropout = dropout if num_layers > 1 else 0.0

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=lstm_dropout,
        )

        self.dropout = nn.Dropout(dropout)

        self.fc1 = nn.Linear(hidden_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):
        """
        x shape:
            (batch_size, sequence_length, input_size)

        output shape:
            (batch_size,)
        """

        lstm_output, _ = self.lstm(x)

        # Use the final timestep representation.
        last_output = lstm_output[:, -1, :]

        x = self.dropout(last_output)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)

        return x.squeeze(-1)