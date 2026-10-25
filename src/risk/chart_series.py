"""
Series behind the dashboard charts.

Every function here turns real inputs (prices, holdings, returns, simulated
paths) into plain lists the frontend can draw. Nothing is invented: when a
series cannot be computed, the caller gets None, not a placeholder value.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm


EWMA_LAMBDA = 0.94
VAR_WINDOW = 252
VAR_CONFIDENCE = 0.95


def portfolio_value_series(price_data, quantities):
    """
    Total value of the holdings on each date.

    price_data: DataFrame with a DATE column and one close-price column per symbol.
    quantities: {symbol: shares}. Value on a date is sum(shares * close).
    """

    closes = price_data.set_index("DATE")[list(quantities)]
    return closes.mul(pd.Series(quantities)).sum(axis=1)


def rebase_to(series, start_value):
    """
    Scale a price series so its first available value equals start_value.
    Dates before the series starts stay missing.
    """

    first = series.dropna()

    if first.empty:
        return series * np.nan

    return series / first.iloc[0] * start_value


def risk_series(returns, window=VAR_WINDOW, confidence=VAR_CONFIDENCE, lambda_=EWMA_LAMBDA):
    """
    One-day 95% VaR thresholds from data known before each day.

    Columns (returns, not losses, so the thresholds are negative):
        RETURN            daily portfolio return
        VAR_EWMA          parametric threshold from the EWMA volatility
        VAR_HISTORICAL    empirical quantile of the previous `window` days
        BREACH            True when the day's return fell below VAR_EWMA

    The first `window` days only seed the estimates, so they are not scored.
    """

    clean = returns.dropna()
    values = clean.to_numpy(dtype=float)
    n = len(values)

    if n <= window:
        raise ValueError(
            f"At least {window + 1} daily returns are needed; got {n}."
        )

    z = norm.ppf(confidence)
    ewma_threshold = np.full(n, np.nan)
    hist_threshold = np.full(n, np.nan)

    variance = np.var(values[:window], ddof=1)

    for t in range(window, n):
        # Estimates use returns up to day t-1 only.
        ewma_threshold[t] = -z * np.sqrt(variance)
        hist_threshold[t] = np.quantile(values[t - window:t], 1 - confidence)
        variance = lambda_ * variance + (1 - lambda_) * values[t] ** 2

    frame = pd.DataFrame({
        "RETURN": values,
        "VAR_EWMA": ewma_threshold,
        "VAR_HISTORICAL": hist_threshold,
    }, index=clean.index)

    scored = frame["VAR_EWMA"].notna()
    frame["BREACH"] = scored & (frame["RETURN"] < frame["VAR_EWMA"])

    return frame


def monte_carlo_fan(simulated_returns, start_value, percentiles=(5, 25, 50, 75, 95)):
    """
    Value percentiles across simulations for each day of the horizon.

    simulated_returns: array of shape (simulations, horizon) of daily returns.
    Day 0 is the starting value.
    """

    returns = np.asarray(simulated_returns, dtype=float)

    if returns.ndim != 2 or returns.shape[0] == 0:
        raise ValueError("simulated_returns must be a non-empty 2-D array.")

    growth = np.cumprod(1 + returns, axis=1)
    paths = np.hstack([np.ones((returns.shape[0], 1)), growth]) * start_value

    fan = {"days": list(range(paths.shape[1]))}

    for p in percentiles:
        fan[f"p{p:02d}"] = [float(v) for v in np.percentile(paths, p, axis=0)]

    return fan


def value_histogram(final_values, bins=24):
    """Counts of simulated end values in equal-width bins."""

    values = np.asarray(final_values, dtype=float)
    counts, edges = np.histogram(values, bins=bins)

    return [
        {
            "low": float(edges[i]),
            "high": float(edges[i + 1]),
            "count": int(counts[i]),
        }
        for i in range(len(counts))
    ]


def to_json_list(values):
    """Convert a numpy/pandas sequence to a list with None for missing values."""

    out = []

    for value in values:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            out.append(None)
        elif isinstance(value, (np.bool_, bool)):
            out.append(bool(value))
        else:
            out.append(float(value))

    return out
