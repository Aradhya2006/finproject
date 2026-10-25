import pandas as pd


MIN_OBSERVATIONS = 30


def calculate_beta(portfolio_returns, benchmark_returns):
    """
    Beta of a return series against a benchmark: cov(p, b) / var(b).

    Only dates present in both series are used. Returns None when there
    are too few overlapping observations or the benchmark has no variance,
    so callers never show a fabricated value.
    """

    aligned = pd.concat(
        [portfolio_returns.rename("portfolio"), benchmark_returns.rename("benchmark")],
        axis=1,
        join="inner",
    ).dropna()

    if len(aligned) < MIN_OBSERVATIONS:
        return None

    benchmark_variance = aligned["benchmark"].var(ddof=1)

    if not benchmark_variance > 0:
        return None

    covariance = aligned["portfolio"].cov(aligned["benchmark"])

    return float(covariance / benchmark_variance)
