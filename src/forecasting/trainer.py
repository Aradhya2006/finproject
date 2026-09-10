import numpy as np
import torch
import torch.nn as nn


def train_lstm(
    model,
    X_train,
    y_train,
    X_validation,
    y_validation,
    epochs=50,
    learning_rate=0.001,
    patience=7,
):
    X_train = np.asarray(
        X_train,
        dtype=np.float32,
    )

    y_train = np.asarray(
        y_train,
        dtype=np.float32,
    )

    X_validation = np.asarray(
        X_validation,
        dtype=np.float32,
    )

    y_validation = np.asarray(
        y_validation,
        dtype=np.float32,
    )

    # -------------------------
    # Validate shapes
    # -------------------------

    if X_train.ndim not in (2, 3):
        raise ValueError(
            "X_train must be a 2D or 3D array."
        )

    if X_validation.ndim != X_train.ndim:
        raise ValueError(
            "X_train and X_validation must "
            "have the same number of dimensions."
        )

    if y_train.ndim != 1:
        raise ValueError(
            "y_train must be a 1D array."
        )

    if y_validation.ndim != 1:
        raise ValueError(
            "y_validation must be a 1D array."
        )

    if len(X_train) != len(y_train):
        raise ValueError(
            "X_train and y_train must contain "
            "the same number of samples."
        )

    if len(X_validation) != len(y_validation):
        raise ValueError(
            "X_validation and y_validation must "
            "contain the same number of samples."
        )

    if len(X_train) == 0:
        raise ValueError(
            "Training data cannot be empty."
        )

    if len(X_validation) == 0:
        raise ValueError(
            "Validation data cannot be empty."
        )

    if epochs <= 0:
        raise ValueError(
            "epochs must be positive."
        )

    if learning_rate <= 0:
        raise ValueError(
            "learning_rate must be positive."
        )

    if patience <= 0:
        raise ValueError(
            "patience must be positive."
        )

    # -------------------------
    # Convert input shape
    # -------------------------

    if X_train.ndim == 2:
        # Original single-feature LSTM:
        # (samples, sequence_length)
        #
        # Convert to:
        # (samples, sequence_length, 1)

        X_train_tensor = torch.tensor(
            X_train,
            dtype=torch.float32,
        ).unsqueeze(-1)

        X_validation_tensor = torch.tensor(
            X_validation,
            dtype=torch.float32,
        ).unsqueeze(-1)

    else:
        # Enhanced multi-feature LSTM:
        # (samples, sequence_length, features)

        X_train_tensor = torch.tensor(
            X_train,
            dtype=torch.float32,
        )

        X_validation_tensor = torch.tensor(
            X_validation,
            dtype=torch.float32,
        )

    y_train_tensor = torch.tensor(
        y_train,
        dtype=torch.float32,
    )

    y_validation_tensor = torch.tensor(
        y_validation,
        dtype=torch.float32,
    )

    # -------------------------
    # Loss and optimizer
    # -------------------------

    criterion = nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
    )

    history = {
        "train_loss": [],
        "validation_loss": [],
    }

    best_validation_loss = float("inf")
    best_state = None
    epochs_without_improvement = 0

    # -------------------------
    # Training loop
    # -------------------------

    for epoch in range(epochs):

        model.train()

        optimizer.zero_grad()

        train_predictions = model(
            X_train_tensor
        )

        train_loss = criterion(
            train_predictions,
            y_train_tensor,
        )

        train_loss.backward()

        optimizer.step()

        # -------------------------
        # Validation
        # -------------------------

        model.eval()

        with torch.no_grad():

            validation_predictions = model(
                X_validation_tensor
            )

            validation_loss = criterion(
                validation_predictions,
                y_validation_tensor,
            )

        train_loss_value = train_loss.item()

        validation_loss_value = (
            validation_loss.item()
        )

        history["train_loss"].append(
            train_loss_value
        )

        history["validation_loss"].append(
            validation_loss_value
        )

        # -------------------------
        # Early stopping
        # -------------------------

        if (
            validation_loss_value
            < best_validation_loss
        ):

            best_validation_loss = (
                validation_loss_value
            )

            best_state = {
                key: value.detach().clone()
                for key, value
                in model.state_dict().items()
            }

            epochs_without_improvement = 0

        else:

            epochs_without_improvement += 1

        if (
            epochs_without_improvement
            >= patience
        ):
            break

    # Restore best model
    if best_state is not None:
        model.load_state_dict(
            best_state
        )

    history["epochs_trained"] = len(
        history["train_loss"]
    )

    history["best_validation_loss"] = (
        best_validation_loss
    )

    return model, history