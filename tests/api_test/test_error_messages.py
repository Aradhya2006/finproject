import re
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app as app_module


@pytest.fixture(autouse=True)
def signed_in_as_admin():
    """These tests check error messages, not sign-in."""
    app_module.app.dependency_overrides[app_module.require_admin] = lambda: None
    yield
    app_module.app.dependency_overrides.clear()


def test_missing_tesseract_returns_503_with_a_clear_message(monkeypatch):
    def no_tesseract(path):
        raise RuntimeError("Tesseract OCR is not installed or not found. Install it, or add its folder to PATH.")

    monkeypatch.setattr(app_module, "extract_holdings_detailed", no_tesseract)

    response = TestClient(app_module.app).post(
        "/api/portfolio/ocr",
        files={"file": ("holdings.png", b"fake image bytes", "image/png")},
    )

    assert response.status_code == 503
    assert "Tesseract OCR is not installed" in response.json()["detail"]


def test_unexpected_fault_names_the_error_type_without_leaking_its_message(monkeypatch):
    def broken(kind, holdings):
        raise RuntimeError("internal path C:/secret/file detail")

    monkeypatch.setattr(app_module, "create_portfolio", broken)
    client = TestClient(app_module.app, raise_server_exceptions=False)

    response = client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}})

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "RuntimeError" in detail
    assert "secret" not in detail


def test_holdings_response_reports_the_oldest_price_date():
    response = TestClient(app_module.app).post("/api/portfolio/holdings", json={"holdings": {"TCS": 10}})

    assert response.status_code == 200
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", response.json()["price_as_of"])
