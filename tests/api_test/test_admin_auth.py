import sqlite3
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app as app_module
from src.auth import admin_sessions, login_limit

PASSWORD = "correct-horse"


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


@pytest.fixture(autouse=True)
def admin_password(monkeypatch, tmp_path):
    monkeypatch.setenv(app_module.ADMIN_PASSWORD_ENV, PASSWORD)
    monkeypatch.setattr(app_module, "create_portfolio", lambda kind, holdings: _stub_portfolio(holdings))
    # Each test gets its own sign-in database and a clean slate for lockouts.
    monkeypatch.setattr(admin_sessions, "DB_PATH", tmp_path / "sessions.db")
    login_limit.reset()


def _login(client, password=PASSWORD):
    return client.post("/api/admin/login", json={"password": password})


def test_save_needs_sign_in():
    response = TestClient(app_module.app).post("/api/portfolio/save", json={"holdings": {"TCS": 10}})

    assert response.status_code == 401


def test_upload_needs_sign_in():
    response = TestClient(app_module.app).post(
        "/api/data/upload",
        data={"symbol": "TCS"},
        files={"file": ("tcs.csv", b"Date,Close\n", "text/csv")},
    )

    assert response.status_code == 401


def test_ocr_needs_sign_in():
    response = TestClient(app_module.app).post(
        "/api/portfolio/ocr",
        files={"file": ("holdings.png", b"not really a png", "image/png")},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("page", ["/admin", "/ingestion", "/risk", "/volatility", "/monte-carlo", "/kinetix", "/overview"])
def test_admin_pages_redirect_to_sign_in(page):
    response = TestClient(app_module.app).get(page, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == f"/login?next={page}"


def test_public_pages_stay_open():
    client = TestClient(app_module.app)

    assert client.get("/").status_code == 200
    assert client.get("/login").status_code == 200


def test_sign_in_refused_when_no_password_is_set(monkeypatch):
    monkeypatch.delenv(app_module.ADMIN_PASSWORD_ENV)

    response = _login(TestClient(app_module.app))

    assert response.status_code == 503
    assert "RISKLENS_ADMIN_PASSWORD" in response.json()["detail"]


def test_wrong_password_is_refused():
    client = TestClient(app_module.app)

    response = _login(client, password="wrong")

    assert response.status_code == 401
    assert app_module.ADMIN_COOKIE not in response.cookies
    assert client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}}).status_code == 401


def test_correct_password_unlocks_writes_and_admin_pages():
    client = TestClient(app_module.app)

    response = _login(client)

    assert response.status_code == 200
    assert app_module.ADMIN_COOKIE in response.cookies
    assert client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}}).status_code == 200
    assert client.get("/ingestion", follow_redirects=False).status_code == 200


def test_logout_locks_writes_again():
    client = TestClient(app_module.app)
    _login(client)

    client.post("/api/admin/logout")

    assert client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}}).status_code == 401
    assert client.get("/ingestion", follow_redirects=False).status_code == 303


def test_sign_in_is_stored_as_a_hash_in_the_database():
    client = TestClient(app_module.app)
    _login(client)
    token = client.cookies.get(app_module.ADMIN_COOKIE)

    with sqlite3.connect(admin_sessions.DB_PATH) as conn:
        stored = [row[0] for row in conn.execute("SELECT token_hash FROM admin_sessions")]

    assert len(stored) == 1
    assert stored[0] != token
    assert admin_sessions.is_valid_session(token)


@pytest.mark.parametrize("method,path", [
    ("GET", "/api/portfolio/current"),
    ("POST", "/api/portfolio/risk"),
    ("POST", "/api/portfolio/series"),
    ("POST", "/api/forecasting/comparison"),
    ("POST", "/api/monte-carlo"),
    ("POST", "/api/scenarios"),
    ("POST", "/api/overview"),
    ("POST", "/api/analyze"),
])
def test_analysis_endpoints_need_sign_in(method, path):
    response = TestClient(app_module.app).request(method, path, json={"holdings": {"TCS": 10}})

    assert response.status_code == 401


def test_home_page_data_stays_open():
    client = TestClient(app_module.app)

    assert client.get("/api/symbols").status_code == 200
    assert client.post("/api/portfolio/holdings", json={"holdings": {"FOO": 1}}).status_code == 200


def test_repeated_wrong_passwords_lock_the_address(monkeypatch):
    monkeypatch.setattr(login_limit, "MAX_FAILURES", 3)
    client = TestClient(app_module.app)

    for _ in range(3):
        assert _login(client, password="wrong").status_code == 401

    locked = _login(client)  # the right password is refused while locked

    assert locked.status_code == 429
    assert "Wait" in locked.json()["detail"]
    assert app_module.ADMIN_COOKIE not in locked.cookies


def test_successful_sign_in_clears_failures(monkeypatch):
    monkeypatch.setattr(login_limit, "MAX_FAILURES", 3)
    client = TestClient(app_module.app)

    _login(client, password="wrong")
    _login(client, password="wrong")
    assert _login(client).status_code == 200

    for _ in range(2):
        assert _login(client, password="wrong").status_code == 401
    assert _login(client).status_code == 200


def test_expired_sign_in_is_refused(monkeypatch):
    monkeypatch.setattr(admin_sessions, "SESSION_SECONDS", -1)
    client = TestClient(app_module.app)
    _login(client)

    assert client.post("/api/portfolio/save", json={"holdings": {"TCS": 10}}).status_code == 401
