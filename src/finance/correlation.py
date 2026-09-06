import pandas as pd


def calculate_covariance_matrix(asset_returns):
    returns = asset_returns.drop(columns="DATE").dropna()

    return returns.cov()


def calculate_correlation_matrix(asset_returns):
    returns = asset_returns.drop(columns="DATE").dropna()

    return returns.corr()