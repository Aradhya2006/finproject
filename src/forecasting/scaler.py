import numpy as np


class StandardScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit(self, X):
        X = np.asarray(X, dtype=np.float32)

        if X.size == 0:
            raise ValueError("Cannot fit scaler on empty data.")

        self.mean_ = np.mean(X)
        self.std_ = np.std(X)

        if self.std_ == 0:
            raise ValueError("Cannot scale data with zero standard deviation.")

        return self

    def transform(self, X):
        if self.mean_ is None or self.std_ is None:
            raise ValueError("Scaler must be fitted before transforming.")

        X = np.asarray(X, dtype=np.float32)

        return (X - self.mean_) / self.std_

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)