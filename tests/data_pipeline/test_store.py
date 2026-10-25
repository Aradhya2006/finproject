import pandas as pd
import pytest

import src.data.loader as loader
import src.data.store as store


def _csv_bytes(frame):
    return frame.to_csv(index=False).encode("utf-8")


def _close_only_frame(days=40, start="2025-01-01"):
    dates = pd.bdate_range(start, periods=days)
    return pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Close": [100 + i * 0.5 for i in range(days)],
    })


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    """Point the loader and store at an empty temporary data folder."""
    monkeypatch.setattr(loader, "RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "RAW_DATA_DIR", tmp_path)
    return tmp_path


def test_symbol_rejects_path_traversal():
    with pytest.raises(ValueError):
        loader.validate_symbol_name("../etc")


def test_symbol_accepts_nse_style_tickers():
    assert loader.validate_symbol_name(" m&m ") == "M&M"
    assert loader.validate_symbol_name("nifty50") == "NIFTY50"


def test_iso_dates_are_read_year_first():
    # 2025-06-12 must be 12 June, not 6 December.
    parsed = store._parse_dates(pd.Series(["2025-06-12"]))

    assert parsed.iloc[0] == pd.Timestamp("2025-06-12")


def test_nse_style_dates_are_read_day_first():
    parsed = store._parse_dates(pd.Series(["12-Jun-2025"]))

    assert parsed.iloc[0] == pd.Timestamp("2025-06-12")


def test_upload_fills_full_nse_schema():
    df = store.normalize_upload(_csv_bytes(_close_only_frame()))

    # SYMBOL is added by save_upload, which knows the ticker.
    for column in store.NSE_COLUMNS:
        if column != "SYMBOL":
            assert column in df.columns
    assert (df["CLOSE"] > 0).all()
    assert (df["HIGH"] >= df["LOW"]).all()


def test_upload_rejects_missing_close_column():
    bad = pd.DataFrame({"Date": ["2025-01-01"], "Open": [1.0]})

    with pytest.raises(ValueError, match="Close"):
        store.normalize_upload(_csv_bytes(bad))


def test_upload_rejects_too_few_rows():
    with pytest.raises(ValueError, match="trading days"):
        store.normalize_upload(_csv_bytes(_close_only_frame(days=5)))


def test_save_upload_is_loadable_and_visible(raw_dir):
    result = store.save_upload("TESTCO", _csv_bytes(_close_only_frame()))

    assert result["has_history"] is True
    assert result["symbol"] == "TESTCO"
    assert store.has_history("TESTCO")
    assert "TESTCO" in [s["symbol"] for s in store.list_symbols()]

    loaded = loader.load_raw_nse_files("TESTCO")
    assert len(loaded) == 40
    assert loaded["DATE"].is_monotonic_increasing


def test_upload_overrides_overlapping_dates(raw_dir):
    first = _close_only_frame(days=30)
    store.save_upload("OVERLAP", _csv_bytes(first))

    revised = first.copy()
    revised["Close"] = revised["Close"] * 2
    store.save_upload("OVERLAP", _csv_bytes(revised))

    loaded = loader.load_raw_nse_files("OVERLAP")

    assert loaded["DATE"].is_unique
    assert loaded["CLOSE"].iloc[-1] == pytest.approx(first["Close"].iloc[-1] * 2)


def test_missing_history_lists_unknown_symbols(raw_dir):
    store.save_upload("KNOWN", _csv_bytes(_close_only_frame()))

    assert store.missing_history(["KNOWN", "UNKNOWN"]) == ["UNKNOWN"]


def test_list_symbols_skips_private_folders(raw_dir):
    (raw_dir / "_archive").mkdir()
    store.save_upload("KNOWN", _csv_bytes(_close_only_frame()))

    names = [s["symbol"] for s in store.list_symbols()]

    assert names == ["KNOWN"]
