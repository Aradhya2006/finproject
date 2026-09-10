import copy

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from src.forecasting.lstm_model import VolatilityLSTM


def set_seed(seed=42):
    """
    Set random seeds for reproducible training.
    """
    np.random.seed(seed)
    torch.manual_seed(seed)


def create_dataloader(X, y, batch_size=32, shuffle=False):
    """
    Convert NumPy arrays into a PyTorch DataLoader.
    """
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    dataset = TensorDataset(X_tensor, y_tensor)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
    )


def train_lstm(
    X_train,
    y_train,
    X_validation,
    y_validation,
    hidden_size=64,
    learning_rate=0.001,
    batch_size=32,
    epochs=100,
    patience=10,
    seed=42,
):
    """
    Train the LSTM using chronological train/validation data.

    Early stopping is based only on validation loss.
    """

    set_seed(seed)

    device = torch.device("cpu")

    model = VolatilityLSTM(
        input_size=X_train.shape[2],
        hidden_size=hidden_size,
    ).to(device)

    train_loader = create_dataloader(
        X_train,
        y_train,
        batch_size=batch_size,
        shuffle=True,
    )

    validation_loader = create_dataloader(
        X_validation,
        y_validation,
        batch_size=batch_size,
        shuffle=False,
    )

    criterion = torch.nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
    )

    best_validation_loss = float("inf")
    best_state = None
    epochs_without_improvement = 0

    history = {
        "train_loss": [],
        "validation_loss": [],
    }

    for epoch in range(epochs):

        # -----------------------------------------------------
        # Training
        # -----------------------------------------------------

        model.train()

        total_train_loss = 0.0
        train_samples = 0

        for X_batch, y_batch in train_loader:

            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()

            predictions = model(X_batch)

            loss = criterion(predictions, y_batch)

            loss.backward()

            optimizer.step()

            batch_size_actual = len(X_batch)

            total_train_loss += loss.item() * batch_size_actual
            train_samples += batch_size_actual

        train_loss = total_train_loss / train_samples

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        model.eval()

        total_validation_loss = 0.0
        validation_samples = 0

        with torch.no_grad():

            for X_batch, y_batch in validation_loader:

                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)

                predictions = model(X_batch)

                loss = criterion(predictions, y_batch)

                batch_size_actual = len(X_batch)

                total_validation_loss += (
                    loss.item() * batch_size_actual
                )

                validation_samples += batch_size_actual

        validation_loss = (
            total_validation_loss / validation_samples
        )

        history["train_loss"].append(train_loss)
        history["validation_loss"].append(validation_loss)

        # -----------------------------------------------------
        # Early stopping
        # -----------------------------------------------------

        if validation_loss < best_validation_loss:

            best_validation_loss = validation_loss

            best_state = copy.deepcopy(model.state_dict())

            epochs_without_improvement = 0

        else:

            epochs_without_improvement += 1

        print(
            f"Epoch {epoch + 1:03d}/{epochs} | "
            f"Train Loss: {train_loss:.6f} | "
            f"Validation Loss: {validation_loss:.6f}"
        )

        if epochs_without_improvement >= patience:

            print(
                f"Early stopping at epoch {epoch + 1}."
            )

            break

    # Restore the best validation model
    if best_state is not None:
        model.load_state_dict(best_state)

    return model, history