"""
Dynamic price-history store.

Discovers which symbols have stored price history, validates user uploads,
and saves them in the NSE schema so the rest of the pipeline can use them
without special cases.
"""

import io
from datetime import datetime

import pandas as pd

from src.data.cleaner import clean_numeric_columns
from src.data.loader import (
    RAW_DATA_DIR,
    load_raw_nse_files,
    normalize_nse_columns,
    validate_symbol_name,
)


# Symbol whose history is used as the market benchmark (beta).
BENCHMARK_SYMBOL = "NIFTY50"

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MIN_UPLOAD_ROWS = 20

# Standard NSE columns in output order.
NSE_COLUMNS = [
    "SYMBOL", "SERIES", "DATE", "PREV. CLOSE", "OPEN", "HIGH", "LOW",
    "LTP", "CLOSE", "VWAP", "VOLUME", "VALUE", "NO. OF TRADES",
    "DELIVERABLE QTY", "DELIVERABLE %",
]

# Columns that may be missing from a simple uploaded file. Each is filled
# from CLOSE (prices) or 0 (counts) so the validator still passes.
PRICE_FALLBACK_COLUMNS = ["OPEN", "HIGH", "LOW", "LTP", "VWAP"]
COUNT_FALLBACK_COLUMNS = ["VOLUME", "VALUE", "NO. OF TRADES", "DELIVERABLE QTY", "DELIVERABLE %"]


def has_history(symbol):
    """True when at least one stored CSV exists for the symbol."""

    try:
        symbol = validate_symbol_name(symbol)
    except ValueError:
        return False

    symbol_dir = RAW_DATA_DIR / symbol

    return symbol_dir.is_dir() and any(
        symbol_dir.glob(f"{symbol}_EQ_*.csv")
    )


def missing_history(symbols):
    """Return the symbols that have no stored price history."""

    return [symbol for symbol in symbols if not has_history(symbol)]


def symbol_status(symbol):
    """Describe the stored history for one symbol."""

    symbol = validate_symbol_name(symbol)

    if not has_history(symbol):
        return {
            "symbol": symbol,
            "has_history": False,
            "rows": 0,
            "first_date": None,
            "last_date": None,
        }

    # Reading every CSV is slow, so the summary is cached until a file for
    # this symbol is added, removed or changed.
    signature = _files_signature(symbol)
    cached = _STATUS_CACHE.get(symbol)
    if cached and cached[0] == signature:
        return dict(cached[1])

    df = load_raw_nse_files(symbol)

    status = {
        "symbol": symbol,
        "has_history": True,
        "rows": int(len(df)),
        "first_date": df["DATE"].min().strftime("%Y-%m-%d"),
        "last_date": df["DATE"].max().strftime("%Y-%m-%d"),
    }
    _STATUS_CACHE[symbol] = (signature, status)
    return dict(status)


_STATUS_CACHE = {}


def _files_signature(symbol):
    """Names and modification times of a symbol's CSV files."""

    symbol_dir = RAW_DATA_DIR / symbol

    return tuple(sorted(
        (path.name, path.stat().st_mtime_ns)
        for path in symbol_dir.glob(f"{symbol}_EQ_*.csv")
    ))


def list_symbols():
    """Every symbol folder in the raw data directory, with its status."""

    if not RAW_DATA_DIR.exists():
        return []

    statuses = []

    for folder in sorted(RAW_DATA_DIR.iterdir()):
        # Folders starting with '_' or '.' are not symbols.
        if not folder.is_dir() or folder.name.startswith(("_", ".")):
            continue

        try:
            statuses.append(symbol_status(folder.name))
        except ValueError as exc:
            statuses.append({
                "symbol": folder.name,
                "has_history": False,
                "rows": 0,
                "first_date": None,
                "last_date": None,
                "error": str(exc),
            })

    return statuses


def _parse_dates(values):
    """
    Parse dates from an upload.

    ISO dates (2025-06-12) are read year-first. Anything else is read
    day-first, which matches NSE exports (12-Jun-2025, 12/06/2025). Reading
    ISO dates day-first would swap day and month.
    """

    values = values.astype(str).str.strip()

    parsed = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    rest = parsed.isna()

    if rest.any():
        try:
            parsed[rest] = pd.to_datetime(
                values[rest], format="mixed", dayfirst=True
            )
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Date column could not be parsed: {exc}") from exc

    return parsed


def normalize_upload(content):
    """
    Parse an uploaded CSV and return it in the full NSE schema.

    Requires a date and a close price column. Other price columns fall back
    to CLOSE and count columns fall back to 0 when absent.
    """

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise ValueError(f"Could not read CSV file: {exc}") from exc

    df = normalize_nse_columns(df)

    if "DATE" not in df.columns or "CLOSE" not in df.columns:
        raise ValueError(
            "CSV must contain a Date column and a Close column "
            f"(found: {', '.join(map(str, df.columns))})."
        )

    df["DATE"] = _parse_dates(df["DATE"])

    df = clean_numeric_columns(df)
    df = df.dropna(subset=["DATE", "CLOSE"])

    if df.empty:
        raise ValueError("No usable rows: Date and Close must be present.")

    df = (
        df.sort_values("DATE", kind="stable")
        .drop_duplicates(subset="DATE", keep="last")
        .reset_index(drop=True)
    )

    if len(df) < MIN_UPLOAD_ROWS:
        raise ValueError(
            f"At least {MIN_UPLOAD_ROWS} trading days are required; found {len(df)}."
        )

    if (df["CLOSE"] <= 0).any():
        raise ValueError("Close prices must be positive.")

    for column in PRICE_FALLBACK_COLUMNS:
        if column not in df.columns:
            df[column] = df["CLOSE"]
        df[column] = df[column].fillna(df["CLOSE"])

    if "PREV. CLOSE" not in df.columns:
        df["PREV. CLOSE"] = df["CLOSE"].shift(1).fillna(df["CLOSE"])

    for column in COUNT_FALLBACK_COLUMNS:
        if column not in df.columns:
            df[column] = 0
        df[column] = df[column].fillna(0)

    if "SERIES" not in df.columns:
        df["SERIES"] = "EQ"

    return df


def save_upload(symbol, content):
    """
    Validate an uploaded CSV for a symbol and store it under the raw data
    directory. Returns a summary of what was stored.
    """

    symbol = validate_symbol_name(symbol)

    if not content:
        raise ValueError("Uploaded file is empty.")

    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Uploaded file is larger than 5 MB.")

    df = normalize_upload(content)

    df["SYMBOL"] = symbol

    symbol_dir = RAW_DATA_DIR / symbol
    symbol_dir.mkdir(parents=True, exist_ok=True)

    first = df["DATE"].min()
    last = df["DATE"].max()
    # Microseconds keep two uploads in the same second from overwriting each other.
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")

    # Name keeps the "{SYMBOL}_EQ_*.csv" pattern the loader searches for.
    file_name = (
        f"{symbol}_EQ_UPLOAD_{first:%d-%m-%Y}_{last:%d-%m-%Y}_{stamp}.csv"
    )

    out = df[NSE_COLUMNS].copy()
    out["DATE"] = out["DATE"].dt.strftime("%d-%b-%Y")
    out.to_csv(symbol_dir / file_name, index=False)

    status = symbol_status(symbol)
    status.update({
        "stored_file": file_name,
        "stored_rows": int(len(df)),
    })
    return status
