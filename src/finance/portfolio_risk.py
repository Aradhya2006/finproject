import numpy as np


def calculate_portfolio_variance(weights, covariance_matrix):
    weight_vector = np.array(
        [
            weights[symbol]
            for symbol in covariance_matrix.columns
        ]
    )

    covariance = covariance_matrix.to_numpy()

    return weight_vector.T @ covariance @ weight_vector


def calculate_portfolio_volatility(
    weights,
    covariance_matrix,
):
    portfolio_variance = calculate_portfolio_variance(
        weights,
        covariance_matrix,
    )

    return np.sqrt(portfolio_variance)