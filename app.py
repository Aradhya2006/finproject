"""RiskLens Quantitative Terminal — Unified API & Dashboard Server

Serves both the quantitative risk APIs and the web terminal pages.
Run with:
    uvicorn app:app --host 0.0.0.0 --port 8000
or
    python app.py
"""

from pathlib import Path
import os
import tempfile
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd
import torch
import uvicorn

# Core RiskLens logic imports
from src.input.portfolio_factory import create_portfolio
from src.input.manual import validate_holdings
from src.input.ocr import extract_holdings_detailed

from src.data.store import (
    BENCHMARK_SYMBOL,
    has_history,
    list_symbols,
    missing_history,
    save_upload,
)
from src.finance.beta import calculate_beta
from src.finance.dataset import create_price_dataset, calculate_asset_returns, load_clean_asset_data
from src.finance.portfolio import calculate_portfolio_returns
from src.finance.correlation import calculate_covariance_matrix, calculate_correlation_matrix
from src.finance.risk_contribution import calculate_percentage_risk_contribution

from src.risk.historical_var import calculate_historical_var
from src.risk.parametric_var import calculate_parametric_var
from src.risk.historical_cvar import calculate_historical_cvar
from src.risk.monte_carlo import (
    simulate_portfolio_returns,
    calculate_cumulative_returns,
    calculate_monte_carlo_var,
    calculate_monte_carlo_cvar,
)
from src.risk.scenario import apply_portfolio_shock, apply_broad_market_shock
from src.risk.chart_series import (
    monte_carlo_fan,
    portfolio_value_series,
    rebase_to,
    risk_series,
    to_json_list,
    value_histogram,
)

from src.forecasting.garch import fit_garch, forecast_garch_volatility
from src.forecasting.baseline_evaluation import evaluate_baseline_models
from src.forecasting.evaluation import calculate_mae, calculate_rmse, calculate_forecast_correlation
from src.forecasting.evaluation_dataset import create_forward_realized_volatility
from src.forecasting.dl_preprocessing import prepare_lstm_data
from src.forecasting.dl_dataset import create_volatility_features
from src.forecasting.lstm_training import train_lstm
from src.forecasting.lstm_evaluation import calculate_lstm_metrics


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Largest screenshot accepted by the OCR endpoint.
MAX_OCR_BYTES = 10 * 1024 * 1024
OCR_IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}

app = FastAPI(title="RiskLens Quantitative Terminal", version="2.0.0")

# Enable CORS for local development and external clients. Credentials are
# not used by the frontend, so they stay off (browsers reject "*" with them).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Sector mapping for equities
SECTOR_MAP = {
    "TCS": "IT",
    "INFY": "IT",
    "HCLTECH": "IT",
    "WIPRO": "IT",
    "RELIANCE": "ENERGY",
    "HDFCBANK": "BANKING",
    "ICICIBANK": "BANKING",
    "SBIN": "BANKING",
}

# No hardcoded portfolio. The session starts empty and is filled by the user
# (manual entry, JSON/CSV paste, or OCR). The browser sends its own holdings
# with each request; the session is only the fallback when none are sent.
session_state: Dict[str, Dict[str, float]] = {"holdings": {}}


def _resolve_holdings(request) -> dict:
    """Holdings from the request body, else the session. Empty if neither."""
    if request and request.holdings:
        return request.holdings
    return session_state["holdings"]

# In-memory cache for slow ML/forecasting models
_FORECAST_CACHE: Dict[str, dict] = {}


def _holdings_cache_key(holdings: dict) -> str:
    return str(sorted(holdings.items()))


def _build_portfolio_and_returns(holdings: dict):
    """
    Shared quantitative setup: build portfolio object, fetch price history,
    and compute individual asset and aggregate returns series.
    """
    missing = missing_history(list(holdings))
    if missing:
        raise ValueError(
            f"No price history for {', '.join(missing)}. "
            "Upload NSE history for these stocks on the Ingestion page first."
        )

    portfolio = create_portfolio("manual", holdings)
    symbols = list(holdings.keys())
    price_data = create_price_dataset(symbols)
    asset_returns = calculate_asset_returns(price_data)

    returns_df = calculate_portfolio_returns(asset_returns, portfolio.weights)
    returns_series = (
        returns_df.set_index("DATE")["PORTFOLIO RETURN"].dropna()
    )

    return portfolio, asset_returns, returns_df, returns_series


# ============================================================
# DATA MODELS
# ============================================================

class HoldingsRequest(BaseModel):
    holdings: Optional[Dict[str, float]] = None


# Periods the user page offers, in trading days.
PERIOD_DAYS = {"1w": 5, "1m": 21, "3m": 63, "6m": 126, "1y": 252}


class PeriodRequest(HoldingsRequest):
    period: str = "1m"


# ============================================================
# HTML DASHBOARD ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def read_home():
    """The user-facing page: enter a portfolio, see the result."""
    path = Path(STATIC_DIR, "home.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/admin", response_class=HTMLResponse)
async def read_admin():
    """Admin tools: data upload, risk models, and the analysis dashboards."""
    path = Path(STATIC_DIR, "admin.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Admin page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/overview", response_class=HTMLResponse)
async def read_overview():
    path = Path(STATIC_DIR, "index.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Overview page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/ingestion", response_class=HTMLResponse)
async def read_ingestion():
    path = Path(STATIC_DIR, "ingestion.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Ingestion page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/risk", response_class=HTMLResponse)
async def read_risk():
    path = Path(STATIC_DIR, "risk.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Risk page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/volatility", response_class=HTMLResponse)
async def read_volatility():
    path = Path(STATIC_DIR, "volatility.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Volatility page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/monte-carlo", response_class=HTMLResponse)
async def read_monte_carlo():
    path = Path(STATIC_DIR, "monte_carlo.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Monte Carlo page not found.")
    return path.read_text(encoding="utf-8")


@app.get("/kinetix", response_class=HTMLResponse)
async def read_kinetix():
    path = Path(STATIC_DIR, "kinetix.html")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Kinetix page not found.")
    return path.read_text(encoding="utf-8")


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok", "app": "RiskLens Quantitative Terminal"}


@app.get("/api/symbols")
def get_symbols():
    """
    Every stock with stored price history, read from the data folder on each
    call, so newly uploaded stocks appear without a restart.
    """
    return {
        "symbols": list_symbols(),
        "benchmark": BENCHMARK_SYMBOL,
        "benchmark_available": has_history(BENCHMARK_SYMBOL),
    }


@app.post("/api/data/upload")
async def upload_price_history(symbol: str = Form(...), file: UploadFile = File(...)):
    """
    Store a daily price CSV for a symbol so it can be valued and analysed.

    Accepts NSE exports and generic files with Date and Close columns.
    Upload the benchmark as symbol NIFTY50 to enable beta.
    """
    try:
        content = await file.read()
        result = save_upload(symbol, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Cached forecasts were built from the old data.
    _FORECAST_CACHE.clear()

    return {"status": "success", **result}


@app.get("/api/portfolio/current")
def get_current_portfolio():
    """Retrieve the current active portfolio stored in session."""
    holdings = session_state["holdings"]
    if not holdings:
        return {
            "status": "empty",
            "holdings": {},
            "rows": [],
            "message": "No holdings yet. Add stocks on the Ingestion page.",
        }
    try:
        portfolio = create_portfolio("manual", holdings)
        price_sources = getattr(portfolio, "price_sources", {})
        rows = [
            {
                "symbol": symbol,
                "sector": SECTOR_MAP.get(symbol, "UNCLASSIFIED"),
                "quantity": portfolio.holdings[symbol],
                "price": portfolio.prices[symbol],
                "value": portfolio.holding_values[symbol],
                "weight": portfolio.weights[symbol],
                "price_source": price_sources.get(symbol, "csv"),
            }
            for symbol in portfolio.assets
        ]
        rows.sort(key=lambda r: r["weight"], reverse=True)
        return {
            "status": "success",
            "portfolio_value": portfolio.portfolio_value,
            "holdings_count": len(portfolio.assets),
            "holdings": holdings,
            "rows": rows,
            "price_sources": price_sources,
            "live_prices": all(
                v == "live" for v in price_sources.values()
            ),
        }
    except Exception as exc:
        return {
            "status": "partial",
            "holdings": holdings,
            "error": str(exc),
        }


@app.post("/api/portfolio/save")
def save_portfolio(request: HoldingsRequest):
    """Save user-updated holdings to current session state."""
    if not request.holdings:
        raise HTTPException(status_code=400, detail="Holdings cannot be empty.")
    try:
        holdings = validate_holdings(request.holdings)
        portfolio = create_portfolio("manual", holdings)
        session_state["holdings"] = holdings
        return {
            "status": "success",
            "portfolio_value": portfolio.portfolio_value,
            "holdings_count": len(portfolio.assets),
            "holdings": holdings,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/portfolio/holdings")
def portfolio_holdings(request: Optional[HoldingsRequest] = None):
    """
    Live portfolio valuation: current closing prices, holding values,
    and weights per symbol. Backs Ingested Asset Validation table.

    Holdings with no stored price history are listed in missing_symbols
    and left out of the valuation, so the rest of the portfolio still shows.
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Holdings cannot be empty.")

    try:
        holdings = validate_holdings(holdings)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    missing = missing_history(list(holdings))
    usable = {symbol: qty for symbol, qty in holdings.items() if symbol not in missing}

    if not usable:
        return {
            "portfolio_value": 0.0,
            "holdings_count": 0,
            "rows": [],
            "missing_symbols": missing,
        }

    try:
        portfolio = create_portfolio("manual", usable)

        rows = []
        for symbol in portfolio.assets:
            rows.append({
                "symbol": symbol,
                "sector": SECTOR_MAP.get(symbol, "UNCLASSIFIED"),
                "quantity": portfolio.holdings[symbol],
                "price": portfolio.prices[symbol],
                "value": portfolio.holding_values[symbol],
                "weight": portfolio.weights[symbol],
                "price_source": getattr(portfolio, "price_sources", {}).get(symbol, "csv"),
            })

        rows.sort(key=lambda r: r["weight"], reverse=True)

        return {
            "portfolio_value": portfolio.portfolio_value,
            "holdings_count": len(portfolio.assets),
            "rows": rows,
            "missing_symbols": missing,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/portfolio/ocr")
async def ocr_upload(file: UploadFile = File(...)):
    """
    Extract portfolio holdings from an uploaded brokerage screenshot (Zerodha Kite, Groww).

    Returns the detected holdings, the real OCR confidence (0-1), and the
    detected tickers that have no stored price history yet (missing_symbols).
    """
    suffix = Path(file.filename or "").suffix.lower() or ".png"
    tmp_path = None

    try:
        if suffix not in OCR_IMAGE_TYPES:
            raise ValueError(f"Unsupported image type '{suffix}'. Use PNG, JPG, BMP, WEBP or TIFF.")

        content = await file.read()

        if not content:
            raise ValueError("Uploaded file is empty.")

        if len(content) > MAX_OCR_BYTES:
            raise ValueError("Screenshot is larger than 10 MB.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = extract_holdings_detailed(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    detected_holdings = result["holdings"]

    # The detected holdings become the session portfolio.
    session_state["holdings"] = detected_holdings

    return {
        "status": "success",
        "detected_holdings": detected_holdings,
        "count": len(detected_holdings),
        "raw_text": result["raw_text"][:500],
        "confidence": result["confidence"],
        "missing_symbols": missing_history(list(detected_holdings)),
    }


@app.post("/api/portfolio/risk")
def portfolio_risk(request: Optional[HoldingsRequest] = None):
    """
    Calculate Static vs Dynamic Risk metrics (VaR 95%, CVaR 95%, Euler risk decomposition).
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Holdings cannot be empty.")

    try:
        portfolio, asset_returns, returns_df, returns_series = _build_portfolio_and_returns(holdings)

        annualized_vol_static = returns_series.std(ddof=1) * np.sqrt(252)

        garch_result = fit_garch(returns_series)
        daily_vol_forecast = float(
            forecast_garch_volatility(garch_result, horizon=1).iloc[0]
        )
        annualized_vol_garch = daily_vol_forecast * np.sqrt(252)

        hist_var = calculate_historical_var(returns_series, confidence_level=0.95)
        param_var = calculate_parametric_var(returns_series, confidence_level=0.95)
        hist_cvar = calculate_historical_cvar(returns_series, confidence_level=0.95)

        # Risk contribution breakdown
        covariance_matrix = calculate_covariance_matrix(asset_returns)
        pct_contribution = calculate_percentage_risk_contribution(
            portfolio.weights, covariance_matrix
        )
        top_symbol = max(pct_contribution, key=pct_contribution.get)

        contributions = [
            {
                "symbol": symbol,
                "sector": SECTOR_MAP.get(symbol, "UNCLASSIFIED"),
                "weight": float(portfolio.weights[symbol]),
                "risk_contribution": float(pct_contribution[symbol]),
                "drag": float(pct_contribution[symbol] - portfolio.weights[symbol]),
            }
            for symbol in portfolio.assets
        ]
        contributions.sort(key=lambda c: c["risk_contribution"], reverse=True)

        return {
            "portfolio_value": portfolio.portfolio_value,
            "weights": portfolio.weights,
            "annualized_volatility_static": float(annualized_vol_static),
            "annualized_volatility_garch": float(annualized_vol_garch),
            "historical_var_95": float(hist_var),
            "historical_var_95_value": float(hist_var * portfolio.portfolio_value),
            "parametric_var_95": float(param_var),
            "parametric_var_95_value": float(param_var * portfolio.portfolio_value),
            "historical_cvar_95": float(hist_cvar),
            "historical_cvar_95_value": float(hist_cvar * portfolio.portfolio_value),
            "top_contributor": {
                "symbol": top_symbol,
                "risk_pct": float(pct_contribution[top_symbol]),
                "weight_pct": float(portfolio.weights[top_symbol]),
                "drag": float(pct_contribution[top_symbol] - portfolio.weights[top_symbol]),
            },
            "contributions": contributions,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/portfolio/series")
def portfolio_series(request: Optional[HoldingsRequest] = None):
    """
    Time series behind the overview and risk charts: holdings value over time,
    the benchmark rebased to the same start, daily returns, and one-day 95% VaR
    thresholds (EWMA and 252-day historical) with the days that breached them.
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Add holdings on the Ingestion page first.")

    try:
        holdings = validate_holdings(holdings)

        missing = missing_history(list(holdings))
        if missing:
            raise ValueError(
                f"No price history for {', '.join(missing)}. "
                "Upload NSE history for these stocks on the Ingestion page first."
            )

        portfolio = create_portfolio("manual", holdings)
        price_data = create_price_dataset(list(holdings))
        asset_returns = calculate_asset_returns(price_data)
        returns_df = calculate_portfolio_returns(asset_returns, portfolio.weights)
        returns = returns_df.set_index("DATE")["PORTFOLIO RETURN"].dropna()

        value = portfolio_value_series(price_data, holdings)
        risk = risk_series(returns)

        benchmark = None
        if has_history(BENCHMARK_SYMBOL):
            closes = load_clean_asset_data(BENCHMARK_SYMBOL).set_index("DATE")["CLOSE"]
            benchmark = closes.reindex(value.index).ffill()
            first_valid = benchmark.first_valid_index()
            if first_valid is not None:
                benchmark = rebase_to(benchmark, value.loc[first_valid])
            else:
                benchmark = None

        latest_threshold = risk["VAR_EWMA"].dropna().iloc[-1]
        scored = risk["VAR_EWMA"].notna()

        return {
            "dates": [d.strftime("%Y-%m-%d") for d in value.index],
            "portfolio_value": to_json_list(value),
            "benchmark": BENCHMARK_SYMBOL if benchmark is not None else None,
            "benchmark_value": to_json_list(benchmark) if benchmark is not None else None,
            "risk_dates": [d.strftime("%Y-%m-%d") for d in risk.index],
            "daily_returns": to_json_list(risk["RETURN"]),
            "var_ewma": to_json_list(risk["VAR_EWMA"]),
            "var_historical": to_json_list(risk["VAR_HISTORICAL"]),
            "breaches": to_json_list(risk["BREACH"]),
            "scored_days": int(scored.sum()),
            "breach_count": int(risk.loc[scored, "BREACH"].sum()),
            "breach_rate_pct": float(risk.loc[scored, "BREACH"].mean() * 100),
            "var_95_pct": float(-latest_threshold),
            "var_95_value": float(-latest_threshold * portfolio.portfolio_value),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/my-portfolio")
def my_portfolio(request: Optional[PeriodRequest] = None):
    """
    Plain-language result for the user-facing page: what the portfolio could be
    worth over the chosen period, how likely a gain is, and how its value has
    moved over the past year. Built from the same simulation as the admin dashboards.
    """
    period = request.period if request else "1m"
    if period not in PERIOD_DAYS:
        raise HTTPException(status_code=400, detail="Choose a period: 1 week, 1 month, 3 months, 6 months or 1 year.")

    simulation = monte_carlo(request, horizon_days=PERIOD_DAYS[period])
    history = portfolio_series(request)

    value_now = simulation["portfolio_value"]
    fan = simulation["fan"]
    last = len(fan["days"]) - 1

    def outcome(value):
        return {"value": value, "change_pct": (value / value_now - 1) * 100}

    past_values = history["portfolio_value"][-252:]
    past_dates = history["dates"][-252:]

    return {
        "value_now": value_now,
        "stock_count": len(_resolve_holdings(request)),
        "period": period,
        "horizon_days": simulation["horizon_days"],
        "average_outcome": outcome(simulation["expected_mean"]["value"]),
        "likely_range": {"low": fan["p25"][last], "high": fan["p75"][last]},
        "wide_range": {"low": fan["p05"][last], "high": fan["p95"][last]},
        "worst_case": outcome(fan["p05"][last]),
        "best_case": outcome(fan["p95"][last]),
        "chance_of_gain_pct": simulation["chance_of_gain_pct"],
        "paths": fan,
        "past": {"dates": past_dates, "values": past_values},
    }


@app.post("/api/forecasting/comparison")
def forecasting_comparison(request: Optional[HoldingsRequest] = None):
    """
    Out-of-sample comparison of Rolling / EWMA / GARCH / LSTM volatility forecasts,
    plus each model's latest T+1 point forecast.
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Holdings cannot be empty.")

    cache_key = _holdings_cache_key(holdings)
    if cache_key in _FORECAST_CACHE:
        return _FORECAST_CACHE[cache_key]

    try:
        portfolio, asset_returns, returns_df, returns_series = _build_portfolio_and_returns(holdings)

        # Leakage-free split
        lstm_data = prepare_lstm_data(
            returns_series,
            lookback=60,
            horizon=21,
            test_months=6,
            validation_ratio=0.15,
        )
        test_dates = lstm_data["dates_test"]

        # Baseline: Rolling + EWMA
        baseline_frame, baseline_results = evaluate_baseline_models(
            returns_series,
            test_dates,
            rolling_window=21,
            ewma_lambda=0.94,
            horizon=21,
        )

        # Baseline: GARCH(1,1)
        garch_result = fit_garch(returns_series)
        garch_vol_series = (
            garch_result.conditional_volatility / 100
        ) * np.sqrt(252)
        garch_vol_series.index = returns_series.dropna().index[-len(garch_vol_series):]

        realized = create_forward_realized_volatility(returns_series, horizon=21)
        aligned_dates = [d for d in test_dates if d in garch_vol_series.index and d in realized.index]
        garch_at_test = garch_vol_series.loc[aligned_dates]
        realized_at_test = realized.loc[aligned_dates]

        garch_results = {
            "observations": len(aligned_dates),
            "mae": float(calculate_mae(realized_at_test, garch_at_test)),
            "rmse": float(calculate_rmse(realized_at_test, garch_at_test)),
            "correlation": float(calculate_forecast_correlation(realized_at_test, garch_at_test)),
        }

        # Deep Learning: LSTM model
        model, history = train_lstm(
            lstm_data["X_train"], lstm_data["y_train"],
            lstm_data["X_validation"], lstm_data["y_validation"],
            hidden_size=32,
            epochs=15,
            patience=5,
        )

        model.eval()
        with torch.no_grad():
            test_tensor = torch.tensor(lstm_data["X_test"], dtype=torch.float32)
            lstm_predictions = model(test_tensor).numpy()

        lstm_metrics = calculate_lstm_metrics(lstm_predictions, lstm_data["y_test"])

        lstm_results = {
            "observations": len(lstm_data["y_test"]),
            "mae": float(lstm_metrics["MAE"]),
            "rmse": float(lstm_metrics["RMSE"]),
            "correlation": float(lstm_metrics["CORR"]),
        }

        # Latest (T+1) point forecasts
        latest_garch_daily = float(
            forecast_garch_volatility(garch_result, horizon=1).iloc[0]
        )
        latest_garch_annualized = latest_garch_daily * np.sqrt(252)

        latest_features = create_volatility_features(returns_series).dropna()
        latest_window = latest_features.iloc[-60:].to_numpy(dtype=np.float32)
        latest_window_scaled = (latest_window - lstm_data["mean"]) / lstm_data["std"]

        model.eval()
        with torch.no_grad():
            latest_tensor = torch.tensor(
                latest_window_scaled[np.newaxis, :, :], dtype=torch.float32
            )
            latest_lstm_forecast = float(model(latest_tensor).item())

        # Chart series: every model over the same dates the LSTM was scored on.
        garch_frame = pd.DataFrame(
            {"garch": garch_at_test.to_numpy()},
            index=pd.to_datetime(aligned_dates),
        )
        lstm_frame = pd.DataFrame(
            {"lstm": np.ravel(lstm_predictions)},
            index=pd.to_datetime(lstm_data["dates_test"]),
        )
        chart_frame = (
            baseline_frame.join(garch_frame, how="inner")
            .join(lstm_frame, how="inner")
            .sort_index()
        )

        result = {
            "series": {
                "dates": [d.strftime("%Y-%m-%d") for d in chart_frame.index],
                "realized": to_json_list(chart_frame["REALIZED"]),
                "rolling": to_json_list(chart_frame["ROLLING"]),
                "ewma": to_json_list(chart_frame["EWMA"]),
                "garch": to_json_list(chart_frame["garch"]),
                "lstm": to_json_list(chart_frame["lstm"]),
            },
            "rolling": baseline_results["ROLLING"],
            "ewma": baseline_results["EWMA"],
            "garch": garch_results,
            "lstm": lstm_results,
            "latest_forecast": {
                "garch_annualized": latest_garch_annualized,
                "lstm_annualized": latest_lstm_forecast,
            },
            "lstm_training": {
                "epochs_run": len(history["train_loss"]),
                "final_validation_loss": float(history["validation_loss"][-1]),
            },
        }
        _FORECAST_CACHE[cache_key] = result
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/monte-carlo")
def monte_carlo(request: Optional[HoldingsRequest] = None, horizon_days: int = 21):
    """
    Monte Carlo portfolio outcome distribution over `horizon_days` trading days:
    expected mean, median, P95, 5% VaR, 95% CVaR, worst simulated path.
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Holdings cannot be empty.")

    try:
        portfolio, asset_returns, returns_df, returns_series = _build_portfolio_and_returns(holdings)
        symbols = list(holdings.keys())

        asset_returns_only = asset_returns.drop(columns="DATE").dropna()
        forecast_vols = asset_returns_only.std(ddof=1) * np.sqrt(252)
        forecast_vols = forecast_vols[symbols]

        correlation_matrix = calculate_correlation_matrix(asset_returns)
        correlation_matrix = correlation_matrix.loc[symbols, symbols]

        simulated_returns = simulate_portfolio_returns(
            forecast_volatilities=forecast_vols,
            correlation_matrix=correlation_matrix,
            weights=portfolio.weights,
            simulations=10000,
            horizon=horizon_days,
            seed=42,
        )

        cumulative = calculate_cumulative_returns(simulated_returns)
        pv = portfolio.portfolio_value

        mc_var = calculate_monte_carlo_var(cumulative, confidence_level=0.95)
        mc_cvar = calculate_monte_carlo_cvar(cumulative, confidence_level=0.95)

        mean_return = float(np.mean(cumulative))
        median_return = float(np.median(cumulative))
        p95_return = float(np.percentile(cumulative, 95))
        worst_return = float(np.min(cumulative))

        return {
            "portfolio_value": pv,
            "expected_mean": {"pct": mean_return, "value": pv * (1 + mean_return)},
            "median": {"pct": median_return, "value": pv * (1 + median_return)},
            "p95_bull_tail": {"pct": p95_return, "value": pv * (1 + p95_return)},
            "var_95": {"pct": float(-mc_var), "value": pv * (1 - mc_var)},
            "cvar_95": {"pct": float(-mc_cvar), "value": pv * (1 - mc_cvar)},
            "worst_path": {"pct": worst_return, "value": pv * (1 + worst_return)},
            "horizon_days": int(simulated_returns.shape[1]),
            "chance_of_gain_pct": float(np.mean(cumulative > 0) * 100),
            "fan": monte_carlo_fan(simulated_returns, pv),
            "histogram": value_histogram(pv * (1 + cumulative)),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/scenarios")
def scenarios(request: Optional[HoldingsRequest] = None):
    """
    Deterministic stress tests for historical/structural market shocks.
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Holdings cannot be empty.")

    try:
        portfolio = create_portfolio("manual", holdings)
        weights = portfolio.weights
        pv = portfolio.portfolio_value

        it_assets = [s for s in weights if SECTOR_MAP.get(s) == "IT"]
        has_reliance = "RELIANCE" in weights

        results = []

        # 1. IT Sector Crash
        shocks = {s: -0.20 for s in it_assets}
        if has_reliance:
            shocks["RELIANCE"] = -0.10
        pct = apply_portfolio_shock(weights, shocks)
        results.append({
            "name": "IT Sector Crash",
            "description": f"IT cohort -20.0%{', Reliance -10.0%' if has_reliance else ''}",
            "pct": pct,
            "value_change": pv * pct,
            "severity_pct": min(100.0, abs(pct) * 450),
        })

        # 2. Broad Market Crash
        pct = apply_broad_market_shock(weights, -0.15)
        results.append({
            "name": "Broad Market Crash",
            "description": f"All {len(weights)} holding assets drop -15.0%",
            "pct": pct,
            "value_change": pv * pct,
            "severity_pct": min(100.0, abs(pct) * 450),
        })

        # 3. Reliance Shock
        shocks = {s: -0.05 for s in it_assets}
        if has_reliance:
            shocks["RELIANCE"] = -0.30
        pct = apply_portfolio_shock(weights, shocks)
        results.append({
            "name": "Reliance Shock",
            "description": f"Reliance -30.0%{', IT cohort -5.0%' if it_assets else ''}",
            "pct": pct,
            "value_change": pv * pct,
            "severity_pct": min(100.0, abs(pct) * 450),
        })

        # 4. Moderate Downturn
        pct = apply_broad_market_shock(weights, -0.10)
        results.append({
            "name": "Moderate Downturn",
            "description": "All holdings drop uniform -10.0%",
            "pct": pct,
            "value_change": pv * pct,
            "severity_pct": min(100.0, abs(pct) * 450),
        })

        return {"portfolio_value": pv, "scenarios": results}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/overview")
@app.post("/api/overview")
def get_overview(request: Optional[HoldingsRequest] = None):
    """
    Combined metrics for the top overview dashboard.

    Beta is measured against the uploaded NIFTY50 history (BENCHMARK_SYMBOL).
    It is null until that history has been uploaded.
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(
            status_code=400,
            detail="Add holdings on the Ingestion page to see the overview.",
        )

    try:
        portfolio, asset_returns, returns_df, returns_series = _build_portfolio_and_returns(holdings)
        pv = portfolio.portfolio_value
        annualized_vol = returns_series.std(ddof=1) * np.sqrt(252)
        mean_annual_return = returns_series.mean() * 252
        sharpe = (mean_annual_return / annualized_vol) if annualized_vol > 0 else 0.0

        beta = None
        if has_history(BENCHMARK_SYMBOL):
            benchmark_returns = (
                load_clean_asset_data(BENCHMARK_SYMBOL)
                .set_index("DATE")["CLOSE"]
                .pct_change()
                .dropna()
            )
            beta = calculate_beta(returns_series, benchmark_returns)

        rows = [
            {
                "symbol": sym,
                "weight": portfolio.weights[sym],
                "value": portfolio.holding_values[sym],
                "quantity": portfolio.holdings[sym],
                "price": portfolio.prices[sym],
            }
            for sym in portfolio.assets
        ]
        rows.sort(key=lambda r: r["value"], reverse=True)

        return {
            "status": "success",
            "portfolio_value": pv,
            "holdings_count": len(rows),
            "holdings": rows,
            "annualized_volatility": float(annualized_vol),
            "sharpe_ratio": float(round(sharpe, 2)),
            "portfolio_beta": None if beta is None else round(beta, 2),
            "benchmark": BENCHMARK_SYMBOL if beta is not None else None,
            "last_day_return": float(returns_series.iloc[-1]),
            "top_holding": rows[0] if rows else None,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/analyze")
def analyze_portfolio(request: HoldingsRequest):
    """
    Simplified plain-language summary endpoint (used by static/kinetix.html).
    """
    holdings = _resolve_holdings(request)
    if not holdings:
        raise HTTPException(status_code=400, detail="Add at least one holding to continue.")

    try:
        holdings = validate_holdings(holdings)
        portfolio = create_portfolio("manual", holdings)
        price_data = create_price_dataset(list(holdings))
        asset_returns = calculate_asset_returns(price_data)
        returns_df = calculate_portfolio_returns(asset_returns, portfolio.weights)
        returns = returns_df["PORTFOLIO RETURN"].dropna()

        rows = [
            {
                "symbol": symbol,
                "quantity": portfolio.holdings[symbol],
                "value": portfolio.holding_values[symbol],
                "weight": portfolio.weights[symbol],
            }
            for symbol in portfolio.assets
        ]
        rows.sort(key=lambda row: row["value"], reverse=True)
        top_positions_weight = sum(row["weight"] for row in rows[:3])
        historical_loss_pct = max(
            0.0,
            float(calculate_historical_var(returns, confidence_level=0.95)),
        )

        return {
            "portfolio_value": portfolio.portfolio_value,
            "holdings_count": len(rows),
            "holdings": rows,
            "largest_holding": rows[0],
            "top_positions_weight": float(top_positions_weight),
            "top_positions_count": min(3, len(rows)),
            "historical_bad_day_loss": float(historical_loss_pct * portfolio.portfolio_value),
            "historical_bad_day_pct": historical_loss_pct,
            "price_history_through": price_data["DATE"].max().strftime("%d %b %Y"),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
