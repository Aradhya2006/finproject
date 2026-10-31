# RiskLens — Quantitative Risk & Volatility Terminal

Quantitative risk analysis, out-of-sample volatility forecasting (Rolling, EWMA, GARCH, LSTM), 10,000-path Merton Jump-Diffusion Monte Carlo simulations, and OCR portfolio ingestion for National Stock Exchange of India (NSE) equities.

Nothing is preloaded. Every figure comes from the price history you upload and the holdings you enter.

---

## Quick Start

Run every command from the project root.

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
OCR screenshots need the Tesseract executable. On Windows it is detected at `C:\Program Files\Tesseract-OCR\tesseract.exe` if it is not on `PATH`.

### 2. Set the admin password
Uploads, saved holdings, the analysis dashboards and OCR need the admin password. The server reads it from `RISKLENS_ADMIN_PASSWORD`. If the variable is empty or not set, admin sign-in is refused.

The easiest place is the `.env` file in the project root. It is git-ignored. Open `.env`, and set:
```
RISKLENS_ADMIN_PASSWORD=choose-a-long-password
```
If `.env` is missing, copy `.env.example` to `.env`. A value already set in the terminal or in Windows settings takes priority over the file.

### 3. Start the server
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```
(`uvicorn api:app ...` and `python app.py` also work.)

### 4. Open the app
- **For users:** <http://localhost:8000/> — enter your stocks, see your result.
- **For the team (admin tools):** <http://localhost:8000/admin>, which links to the dashboards:
  - Stock data and holdings: <http://localhost:8000/ingestion>
  - Overview, risk, volatility, Monte Carlo, quick summary: `/overview`, `/risk`, `/volatility`, `/monte-carlo`, `/kinetix`

---

## For Users

The home page is deliberately simple. The user:

1. **Adds stocks.** Choose a stock from the list and enter the number of shares. Only stocks the team has loaded are listed.
2. **Reads the result.** The page shows the average outcome for the next month, the chance of making money, the likely range, a bad-month figure, a graph of possible paths, and how the portfolio moved over the past year.

The browser keeps the portfolio in local storage. Nothing about models or data sources is shown on the user page.

## For the Team (Admin Tools)

1. **Upload price history.** On *Stock data and holdings*, enter a ticker and choose a daily CSV, then click *Upload History*. The file needs a Date column and a Close column. NSE exports work as they are. Each stock needs its own upload before users can choose it.
2. **Enable beta (optional).** Upload the NIFTY 50 index file with ticker `NIFTY50`. Beta on the overview is then measured against it. Until then it shows as `—`.
3. **Use the dashboards.** Risk, volatility and Monte Carlo use the same holdings and history.
4. **Holdings in the admin tools** can also be entered from a screenshot (OCR) or as JSON/CSV. Check OCR quantities before relying on them.

The admin pages are not linked from the user page. They redirect to `/login`. Uploads, saved holdings, OCR and the analysis endpoints require the admin password. Only the home page's own data (the stock list, the valuation and the plain-language result) is open. Sign-in lasts 12 hours, or until you sign out (`POST /api/admin/logout`). Sign-ins are stored in `data/risklens.db` (SQLite, git-ignored) as hashes, so they survive a server restart. Five wrong passwords from one address lock that address out for 15 minutes. The lockout counts are kept in memory, so they reset on restart. The server sends no cross-site access headers, so other websites cannot call the API from a browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` `/ingestion` `/risk` `/volatility` `/monte-carlo` `/kinetix` | Pages (served from `static/`) |
| `GET` | `/health` | Service health |
| `GET` | `/api/symbols` | Every stock with stored history (rows, first and last date), and benchmark status |
| `POST` | `/api/admin/login` | Sign in as admin with `{"password": ...}`. Sets an httponly cookie |
| `POST` | `/api/admin/logout` | Sign out |
| `POST` | `/api/data/upload` | **Admin.** Store a daily price CSV for one ticker (`multipart/form-data`: `symbol`, `file`). Max 5 MB |
| `POST` | `/api/portfolio/holdings` | Valuation of the holdings that have history. Lists the rest in `missing_symbols` |
| `POST` | `/api/portfolio/ocr` | **Admin.** Screenshot → holdings, with real OCR confidence, raw text and `missing_symbols`. Max 10 MB |
| `POST` | `/api/portfolio/save` | **Admin.** Save holdings to this browser's server session (a cookie identifies the browser) |
| `GET` | `/api/portfolio/current` | This browser's session portfolio and valuation (`status: "empty"` when none) |
| `POST` | `/api/portfolio/risk` | **Admin.** Historical VaR 95%, parametric VaR, CVaR 95%, GARCH σ, Euler risk breakdown |
| `POST` | `/api/forecasting/comparison` | **Admin.** Out-of-sample MAE / RMSE / correlation for Rolling, EWMA, GARCH, LSTM, plus T+1 forecasts |
| `POST` | `/api/monte-carlo` | **Admin.** 10,000 Merton jump-diffusion paths: mean, median, P95, VaR and CVaR, worst path |
| `POST` | `/api/scenarios` | **Admin.** Deterministic stress tests (IT crash, broad crash, Reliance shock, moderate downturn) |
| `GET` `POST` | `/api/overview` | **Admin.** Equity, Sharpe, beta vs NIFTY50 (null until uploaded), last-day return |
| `POST` | `/api/analyze` | **Admin.** Plain-language downside and concentration summary |
| `POST` | `/api/my-portfolio` | User-page result: average outcome, chance of gain, likely and bad-month ranges, paths, and the past year |

Analysis endpoints return HTTP 400 with a message when a holding has no history, for example `No price history for FOO. Upload NSE history …`. Bad input gets HTTP 400. A setup problem, such as Tesseract missing for OCR, gets HTTP 503 with a message that says what to install. An unexpected server fault gets HTTP 500 with the error type. The full traceback is in the server log.

---

## Project Structure

```
risklens2/
├── app.py                        # FastAPI server: API and page routes
├── api.py                        # Alias that re-exports app (uvicorn api:app)
├── requirements.txt
├── requirements-dev.txt          # Adds the test dependencies (httpx)
├── pytest.ini
├── static/                       # Frontend, served by app.py
│   ├── home.html / home.js       # User page: enter stocks, see the result
│   ├── admin.html                # Index of the admin tools
│   ├── charts.js                 # Shared chart drawing (used by both)
│   ├── index.html                # Overview (admin)
│   ├── ingestion.html            # Holdings, OCR, price-history upload
│   ├── risk.html                 # Static & dynamic risk
│   ├── volatility.html           # Volatility models
│   ├── monte_carlo.html          # Monte Carlo & stress tests
│   ├── kinetix.html              # Quick summary
│   └── terminal.js               # Client bridge: calls the API and fills the pages
├── src/
│   ├── data/                     # loader (stored CSVs), store (uploads, symbol list),
│   │                             # cleaner, validator, current_prices (live NSE + CSV fallback)
│   ├── finance/                  # returns, covariance, Euler risk contribution, beta
│   ├── risk/                     # historical / parametric / Monte Carlo VaR, CVaR, dynamic risk, backtests
│   ├── forecasting/              # GARCH(1,1), EWMA, rolling, LSTM (PyTorch)
│   └── input/                    # manual holdings, OCR (ocr.py, ocr_engine.py), verification
├── data/
│   ├── raw/nse/<SYMBOL>/         # Daily CSVs per stock. Uploads are saved here as <SYMBOL>_EQ_UPLOAD_*.csv
│   └── processed/
├── scripts/                      # Research and maintenance scripts (run from the project root)
│   └── check_frontend_wiring.py  # Verifies every element id and API route the frontend uses
├── tests/                        # pytest suite (data_pipeline, finance_test, forecasting_test, dynamic_engine)
├── outputs/                      # Generated figures
├── design/                       # Stitch design exports (reference only, not served)
├── notebooks/
└── SESSION_LOG.md                # Running record of changes and outcomes
```

---

## Checks

Install the test extras once (adds `httpx`, which the API tests need):
```bash
pip install -r requirements-dev.txt
```

Run the test suite:
```bash
pytest
```
The suite has 207 tests. They cover finance, risk, forecasting, OCR, the upload store, beta, and the API. The full run takes about 7 minutes. The slow tests (the LSTM tests and four long risk backtests) are marked `slow`. For a quick run that skips them:
```bash
pytest -m "not slow"
```

Check that the frontend and backend still match:
```bash
python scripts/check_frontend_wiring.py
```
It fails if a page writes to an element id that does not exist, or calls an API route that is not defined.

---

## Known Limits

- **Live prices** come from the NSE website, which is unofficial and often blocks scripted requests. When the live call fails, the latest stored closing price is used, and the table labels the source as `CSV`.
- **Stored history ends at the last uploaded date.** The bundled NSE files end in September 2026. The Ingestion page shows the date of the oldest stored price used in the valuation, and warns when it is over 30 days old. Live NSE prices often return HTTP 403, so valuations usually use stored closes. Upload the latest daily CSV to update them.
- **Beta** needs a NIFTY50 upload with at least 30 overlapping trading days.
- **Stress scenarios** use fixed shock sizes defined in `app.py`. They are scenario definitions, not market data.
- **Charts are drawn from your data:** the overview equity curve, holdings donut and sparkline; the risk return and VaR chart; the volatility model comparison; the Monte Carlo fan chart and outcome histogram.
- **The volatility page figures are computed** from the out-of-sample test window (about six months). Directional accuracy, the Spearman correlation, the RMSE gap, the regime shares and the static volatility all come from the stored history.
- **Some risk and Monte Carlo figures are still design placeholders** (for example "-3.53% GARCH", "Static 1.91%" and the rupee values on the Monte Carlo page). They are not computed yet, so do not read them as results.
