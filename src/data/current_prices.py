"""
Live NSE price fetching with CSV fallback.

Attempts to fetch real-time quotes from the NSE API first.
Falls back to the latest stored CSV price if the live fetch fails.
Historical CSV data is always used for returns/risk calculations.
"""

import logging
from src.data.cleaner import (
    clean_dates,
    clean_numeric_columns,
)
from src.data.loader import load_raw_nse_files

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Live NSE quote endpoint (no auth required, only needs cookie session)
# ---------------------------------------------------------------------------
_NSE_BASE = "https://www.nseindia.com"
_NSE_QUOTE_URL = f"{_NSE_BASE}/api/quote-equity"
_NSE_MARKET_URL = f"{_NSE_BASE}/market-data/live-equity-market"

# cached live prices to avoid hammering NSE on every request
_LIVE_CACHE: dict = {}
_LIVE_MISSES: set = set()  # symbols whose live fetch failed within the TTL window
_LIVE_CACHE_TS: float = 0.0
_LIVE_CACHE_TTL: float = 60.0  # seconds before cache expires


def _create_live_session():
    """Build an NSE requests.Session that mimics a browser."""
    import requests

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": _NSE_BASE + "/",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        }
    )
    return session


def _warm_nse_session(session) -> bool:
    """
    Hit the NSE homepage to obtain session cookies.
    Required before any API calls.
    """
    try:
        r = session.get(_NSE_BASE + "/", timeout=10)
        r.raise_for_status()
        return True
    except Exception as exc:
        logger.warning("NSE session warm-up failed: %s", exc)
        return False


def fetch_live_nse_price(symbol: str) -> float | None:
    """
    Fetch the current-day last traded price for *symbol* from NSE.

    Returns
    -------
    float | None
        Last traded price on success, None on any failure.
        Does NOT write anything to disk.
    """
    import requests

    symbol = symbol.strip().upper()
    session = _create_live_session()

    # Warm up the session (get cookies)
    if not _warm_nse_session(session):
        return None

    try:
        resp = session.get(
            _NSE_QUOTE_URL,
            params={"symbol": symbol},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        # NSE API returns {"priceInfo": {"lastPrice": ...}, ...}
        price_info = data.get("priceInfo", {})
        last_price = price_info.get("lastPrice") or price_info.get("close")

        if last_price and float(last_price) > 0:
            logger.info("Live NSE price for %s: %s", symbol, last_price)
            return float(last_price)

    except requests.exceptions.RequestException as exc:
        logger.warning("Live NSE request failed for %s: %s", symbol, exc)
    except (ValueError, KeyError, TypeError) as exc:
        logger.warning("Live NSE parse error for %s: %s", symbol, exc)

    return None


def _get_csv_price(symbol: str) -> float:
    """
    Fallback: get the latest closing price from stored NSE CSV files.
    Raises ValueError if no data is found.
    """
    df = load_raw_nse_files(symbol)

    if df.empty:
        raise ValueError(f"No data found for {symbol}.")

    if "DATE" not in df.columns:
        raise ValueError(f"DATE column missing for {symbol}.")

    if "CLOSE" not in df.columns:
        raise ValueError(f"CLOSE column missing for {symbol}.")

    df = df.copy()
    df = clean_dates(df)
    df = clean_numeric_columns(df)
    df = df.dropna(subset=["DATE", "CLOSE"]).sort_values("DATE")

    if df.empty:
        raise ValueError(f"No valid price data for {symbol}.")

    latest_price = float(df.iloc[-1]["CLOSE"])

    if latest_price <= 0:
        raise ValueError(f"Invalid latest price for {symbol}.")

    return latest_price


def get_latest_prices(symbols) -> dict:
    """
    Get the latest NSE price for each symbol.

    Tries the live NSE API first (no disk write).
    Falls back to the most-recent row in stored CSV files.

    Parameters
    ----------
    symbols : list
        NSE ticker symbols (e.g. ["TCS", "INFY"]).

    Returns
    -------
    dict
        {symbol: price} mapping with source annotation under
        the key ``_sources`` (dict of symbol -> "live" | "csv").
    """
    import time as _time

    if not isinstance(symbols, list):
        raise ValueError("symbols must be a list.")

    if not symbols:
        raise ValueError("symbols cannot be empty.")

    normalized = []
    for sym in symbols:
        if not isinstance(sym, str):
            raise ValueError("Symbols must be strings.")
        sym = sym.strip().upper()
        if not sym:
            raise ValueError("Symbol cannot be empty.")
        normalized.append(sym)

    global _LIVE_CACHE, _LIVE_MISSES, _LIVE_CACHE_TS

    # Refresh live cache if stale
    cache_age = _time.time() - _LIVE_CACHE_TS
    if cache_age > _LIVE_CACHE_TTL:
        _LIVE_CACHE = {}
        _LIVE_MISSES = set()
        _LIVE_CACHE_TS = _time.time()

    prices: dict = {}
    sources: dict = {}

    for symbol in normalized:
        # 1. Try live price (cached within TTL window, failures included)
        if symbol not in _LIVE_CACHE and symbol not in _LIVE_MISSES:
            live_price = fetch_live_nse_price(symbol)
            if live_price is not None:
                _LIVE_CACHE[symbol] = live_price
            else:
                _LIVE_MISSES.add(symbol)

        if symbol in _LIVE_CACHE:
            prices[symbol] = _LIVE_CACHE[symbol]
            sources[symbol] = "live"
            continue

        # 2. Fall back to CSV
        try:
            csv_price = _get_csv_price(symbol)
            prices[symbol] = csv_price
            sources[symbol] = "csv"
            logger.info(
                "Using stored CSV price for %s: %s",
                symbol,
                csv_price,
            )
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    prices["_sources"] = sources
    return prices