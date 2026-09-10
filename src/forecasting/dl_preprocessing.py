import numpy as np
import pandas as pd

from src.forecasting.dl_dataset import create_lstm_sequences


def prepare_lstm_data(
    returns,
    lookback=60,
    horizon=21,
    test_months=6,
    validation_ratio=0.15,
):
    """
    Create leakage-free train, validation, and test datasets.

    Test set:
        Last `test_months` of prediction dates.

    Validation set:
        `validation_ratio` of the data immediately before the test set.

    Scaling:
        Mean and standard deviation are calculated using training
        observations only.
    """

    if test_months <= 0:
        raise ValueError("test_months must be greater than zero.")

    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio must be between 0 and 1.")

    X, y, dates = create_lstm_sequences(
        returns,
        lookback=lookback,
        horizon=horizon,
    )

    # ---------------------------------------------------------
    # 1. Identify the final 6-month test period
    # ---------------------------------------------------------

    test_start = dates.max() - pd.DateOffset(months=test_months)

    test_mask = dates >= test_start
    pre_test_mask = dates < test_start

    if test_mask.sum() == 0:
        raise ValueError("Test set is empty.")

    # ---------------------------------------------------------
    # 2. Split the pre-test data chronologically
    # ---------------------------------------------------------

    pre_test_indices = np.where(pre_test_mask)[0]

    validation_size = int(
        len(pre_test_indices) * validation_ratio
    )

    if validation_size == 0:
        raise ValueError("Validation set is empty.")

    train_indices = pre_test_indices[:-validation_size]
    validation_indices = pre_test_indices[-validation_size:]

    if len(train_indices) == 0:
        raise ValueError("Training set is empty.")

    # ---------------------------------------------------------
    # 3. Extract datasets
    # ---------------------------------------------------------

    X_train = X[train_indices]
    y_train = y[train_indices]
    dates_train = dates[train_indices]

    X_validation = X[validation_indices]
    y_validation = y[validation_indices]
    dates_validation = dates[validation_indices]

    test_indices = np.where(test_mask)[0]

    X_test = X[test_indices]
    y_test = y[test_indices]
    dates_test = dates[test_indices]


    # ---------------------------------------------------------
    # 4. Fit scaler ONLY on training data
    # ---------------------------------------------------------

    n_features = X_train.shape[2]

    training_values = X_train.reshape(-1, n_features)

    mean = training_values.mean(axis=0)
    std = training_values.std(axis=0)

    # Prevent division by zero
    std[std == 0] = 1.0

    # ---------------------------------------------------------
    # 5. Apply training scaler to all inputs
    # ---------------------------------------------------------

    X_train = (X_train - mean) / std
    X_validation = (X_validation - mean) / std
    X_test = (X_test - mean) / std

    return {
        "X_train": X_train.astype(np.float32),
        "y_train": y_train.astype(np.float32),
        "dates_train": dates_train,

        "X_validation": X_validation.astype(np.float32),
        "y_validation": y_validation.astype(np.float32),
        "dates_validation": dates_validation,

        "X_test": X_test.astype(np.float32),
        "y_test": y_test.astype(np.float32),
        "dates_test": dates_test,

        "mean": mean,
        "std": std,
    }