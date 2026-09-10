def chronological_split(
    X,
    y,
    dates,
    train_ratio=0.70,
    validation_ratio=0.15,
):
    if not 0 < train_ratio < 1:
        raise ValueError(
            "train_ratio must be between 0 and 1."
        )

    if not 0 < validation_ratio < 1:
        raise ValueError(
            "validation_ratio must be between 0 and 1."
        )

    if train_ratio + validation_ratio >= 1:
        raise ValueError(
            "train_ratio + validation_ratio must be less than 1."
        )

    if len(X) != len(y) or len(X) != len(dates):
        raise ValueError(
            "X, y, and dates must have the same length."
        )

    if len(X) == 0:
        raise ValueError(
            "Dataset cannot be empty."
        )

    train_end = int(len(X) * train_ratio)

    validation_end = int(
        len(X) * (train_ratio + validation_ratio)
    )

    # Training set
    X_train = X[:train_end]
    y_train = y[:train_end]
    dates_train = dates[:train_end]

    # Validation set
    X_validation = X[train_end:validation_end]
    y_validation = y[train_end:validation_end]
    dates_validation = dates[train_end:validation_end]

    # Test set
    X_test = X[validation_end:]
    y_test = y[validation_end:]
    dates_test = dates[validation_end:]

    return (
        X_train,
        y_train,
        dates_train,
        X_validation,
        y_validation,
        dates_validation,
        X_test,
        y_test,
        dates_test,
    )