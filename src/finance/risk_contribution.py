import numpy as np


def calculate_marginal_risk_contribution(
    weights,
    covariance_matrix,
):
    weight_vector = np.array(
        [
            weights[symbol]
            for symbol in covariance_matrix.columns
        ]
    )

    covariance = covariance_matrix.to_numpy()

    portfolio_variance = (
        weight_vector.T
        @ covariance
        @ weight_vector
    )

    portfolio_volatility = np.sqrt(
        portfolio_variance
    )

    marginal_contribution = (
        covariance @ weight_vector
    ) / portfolio_volatility

    return {
        symbol: marginal_contribution[i]
        for i, symbol in enumerate(
            covariance_matrix.columns
        )
    }


def calculate_component_risk_contribution(
    weights,
    covariance_matrix,
):
    marginal_contribution = (
        calculate_marginal_risk_contribution(
            weights,
            covariance_matrix,
        )
    )

    component_contribution = {
        symbol:
        weights[symbol] * marginal_contribution[symbol]
        for symbol in weights
    }

    return component_contribution


def calculate_percentage_risk_contribution(
    weights,
    covariance_matrix,
):
    component_contribution = (
        calculate_component_risk_contribution(
            weights,
            covariance_matrix,
        )
    )

    total_risk = sum(
        component_contribution.values()
    )

    return {
        symbol:
        contribution / total_risk
        for symbol, contribution
        in component_contribution.items()
    }