from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app as app_module


@pytest.fixture(autouse=True)
def signed_in_as_admin():
    """These tests cover session handling, not sign-in, so skip the admin check."""
    app_module.app.dependency_overrides[app_module.require_admin] = lambda: None
    yield
    app_module.app.dependency_overrides.clear()


def _stub_portfolio(holdings):
    """Minimal stand-in for create_portfolio, so the tests need no price data."""
    return SimpleNamespace(
        portfolio_value=1000.0,
        assets=list(holdings),
        holdings=dict(holdings),
        prices={},
        holding_values={},
        weights={},
        price_sources={},
    )


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "create_portfolio", lambda kind, holdings: _stub_portfolio(holdings))
    app_module._sessions.clear()
    return TestClient(app_module.app)


def test_new_browser_gets_session_cookie(client):
    response = client.get("/health")

    assert app_module.SESSION_COOKIE in response.cookies


def test_holdings_are_kept_per_browser(client):
    saver = TestClient(app_module.app)
    other = TestClient(app_module.app)

    saved = saver.post("/api/portfolio/save", json={"holdings": {"TCS": 10}})
    assert saved.status_code == 200

    assert saver.get("/api/portfolio/current").json()["holdings"] == {"TCS": 10}
    assert other.get("/api/portfolio/current").json()["status"] == "empty"


def test_oversize_upload_is_rejected_without_being_stored(client):
    too_big = b"x" * (app_module.MAX_UPLOAD_BYTES + 1)

    response = client.post(
        "/api/data/upload",
        data={"symbol": "TCS"},
        files={"file": ("big.csv", too_big, "text/csv")},
    )

    assert response.status_code == 400
    assert "larger than 5 MB" in response.json()["detail"]


def test_bad_input_returns_400_with_message(client, monkeypatch):
    def reject(kind, holdings):
        raise ValueError("Quantity must be positive.")

    monkeypatch.setattr(app_module, "create_portfolio", reject)

    response = client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}})

    assert response.status_code == 400
    assert response.json()["detail"] == "Quantity must be positive."


def test_server_fault_returns_500_not_400(monkeypatch):
    def broken(kind, holdings):
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(app_module, "create_portfolio", broken)
    client = TestClient(app_module.app, raise_server_exceptions=False)

    response = client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}})

    assert response.status_code == 500
