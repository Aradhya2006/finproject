"""
Summary figures for the volatility benchmark page. Each one is computed from
the out-of-sample forecasts or from the portfolio's return history.
"""

import numpy as np
import pandas as pd


TRADING_DAYS = 252

# Volatility bands (annualized) used for the regime view. The thresholds are fixed.
LOW_VOL = 0.14
HIGH_VOL = 0.22
REGIME_WINDOW = 21
REGIMES = ("low", "normal", "high")


def directional_accuracy(realized, forecast):
    """
    Share of days where the forecast moved the same way as realized volatility
    (up, down or flat), day over day. Returns None when there are too few days.
    """
    frame = pd.concat([realized, forecast], axis=1).dropna()
    changes = frame.diff().dropna()
    if changes.empty:
        return None

    same_direction = np.sign(changes.iloc[:, 0]) == np.sign(changes.iloc[:, 1])
    return float(same_direction.mean())


def rank_correlation(realized, forecast):
    """Spearman rank correlation between realized volatility and a forecast."""
    frame = pd.concat([realized, forecast], axis=1).dropna()
    if len(frame) < 3:
        return None
    return float(frame.iloc[:, 0].corr(frame.iloc[:, 1], method="spearman"))


def volatility_regimes(returns):
    """
    Share of days in each volatility band, the chance that a day stays in the
    same band the next day, and the band of the latest day.
    """
    vol = returns.rolling(REGIME_WINDOW).std(ddof=1).dropna() * np.sqrt(TRADING_DAYS)
    if vol.empty:
        return None

    labels = np.select([vol < LOW_VOL, vol > HIGH_VOL], ["low", "high"], default="normal")
    current, following = labels[:-1], labels[1:]

    shares = {name: float(np.mean(labels == name)) for name in REGIMES}
    stay = {}
    for name in REGIMES:
        leaving = current == name
        stay[name] = float(np.mean(following[leaving] == name)) if leaving.any() else None

    return {"shares": shares, "stay": stay, "current": str(labels[-1])}


def benchmark_summary(chart_frame, garch_results, lstm_results):
    """
    Figures quoted beside the model table. `chart_frame` holds the realized
    volatility and each model's forecast on the same test dates.
    """
    realized = chart_frame["REALIZED"]
    models = {"rolling": "ROLLING", "ewma": "EWMA", "garch": "garch", "lstm": "lstm"}

    directional = {
        name: directional_accuracy(realized, chart_frame[column])
        for name, column in models.items()
    }

    garch_rmse = garch_results["rmse"]
    lstm_rmse = lstm_results["rmse"]
    rmse_gap_pct = (garch_rmse - lstm_rmse) / lstm_rmse * 100 if lstm_rmse else None

    return {
        "directional_accuracy": directional,
        "lstm_spearman": rank_correlation(realized, chart_frame["lstm"]),
        "garch_rmse_vs_lstm_pct": rmse_gap_pct,
        "latest_ewma": float(chart_frame["EWMA"].iloc[-1]),
    }
