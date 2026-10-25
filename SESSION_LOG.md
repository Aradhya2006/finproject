# RiskLens — Session Log

Running record of what was checked, what was changed, and what happened afterwards.
Newest session first.

---

## Session 5 — 2026-10-25 (simple user page, admin tools separated)

Request: the user should see a simple page where they enter their portfolio and get a
result they can understand from a graph (how much they could make). The backend stays
for the team; the user should not see it.

**Changes**
- `static/home.html` + `static/home.js` (new): the user page at `/`. Steps: choose a stock from the list and enter shares; then see the average outcome for about one month, the chance of making money, the likely range (9 months in 10), a bad-month figure, a graph of possible paths, and the past year's value. Plain language only. No model names, endpoints or data sources.
- `static/admin.html` (new): index of the admin tools at `/admin`, which the user page does not link to.
- Old overview moved to `/overview`. Admin pages link to it. Ingestion, risk, volatility, Monte Carlo and quick summary are unchanged and still at their routes.
- `app.py`:
  - `/` serves the user page; `/admin` and `/overview` added.
  - `POST /api/my-portfolio` returns the user result (built on the same simulation and history).
  - Monte Carlo response includes `chance_of_gain_pct`.
- `static/charts.js` (new): the chart drawing moved out of `terminal.js` so both pages can use it. Its labels no longer depend on `RiskLens`.
- `/api/symbols` now caches each stock's summary until its files change. It took about 2.4 s on every call; repeat calls now take about 8 ms.
- `scripts/check_frontend_wiring.py` also checks `home.js` ids and API calls.

**Checks**
- User page (jsdom against the live server): 15 of 15 pass. Covers the stock list, the result after adding stocks, plain-language headline, average outcome, chance, ranges, both charts, a share change refreshing the result, and removing a stock. No model or technical words appear on the page.
- Admin browser smoke test: 39 of 39 pass, with the overview now at `/overview`.
- Wiring audit: passes.
- Full pytest suite: see the result reported in this session.

**Notes**
- The "average outcome" is the mean of the simulation. It is an estimate from past price moves, not a promise. The page says so.
- Still no login: `/admin` is only hidden, not protected. Add authentication before sharing the app.

---

## Session 4 — 2026-10-25 (manual add fix)

Report: the user could not add stocks manually.

**Cause (reproduced in jsdom against the live server):** adding a ticker with no stored price history saved it to the browser, but the row never appeared in the table. Missing stocks were only named in the warning banner, so the add looked like it did nothing. The add also relied on two browser `prompt()` dialogs, which are easy to dismiss or block.

**Changes**
- `static/ingestion.html`: the Manual tab now has a ticker field, a quantity field and an *Add to Portfolio* button, with an inline error line.
- `static/terminal.js`:
  - `addManualHolding()` replaces the prompts. It validates the ticker and quantity, saves, re-values, and clears the form. Enter also submits.
  - `renderHoldingsTable()` lists stocks with no history as rows marked `NO DATA`, with an editable quantity and `—` for price, value and weight. The valued stocks are listed first.

**Checks**
- Reproduction after the fix: a bad ticker and a zero quantity each show an inline error. A valid ticker appears in the table at once as `NO DATA`, with its quantity. The banner still explains what to upload.
- Browser smoke test: 39 of 39 pass. Wiring audit passes.
- A doubled add seen in one test run was a test artifact: jsdom fired `DOMContentLoaded` twice. Without the manual dispatch, the quantity is correct.

---

## Session 3 — 2026-10-25 (live charts)

Request: make the charts live, so they are drawn from data rather than fixed SVG shapes.

### 1. Charts changed

| Page | Chart | Data source |
|---|---|---|
| Overview | Equity curve (holdings value over time, benchmark dashed if NIFTY50 uploaded) | `POST /api/portfolio/series` |
| Overview | Allocation donut and its legend (one arc and row per holding) | `/api/overview` holdings weights |
| Overview | Sparkline (last 20 values) | `/api/portfolio/series` |
| Risk | Daily returns with EWMA and 252-day historical 95% VaR thresholds; breaches marked | `/api/portfolio/series` |
| Risk | Breach-rate pill | `breach_rate_pct` from the same endpoint |
| Volatility | Realised vs Rolling, EWMA, GARCH and LSTM over the same test dates | `/api/forecasting/comparison` → `series` |
| Monte Carlo | 21-day fan chart (5–95% and 25–75% bands, median) | `/api/monte-carlo` → `fan` |
| Monte Carlo | Outcome histogram (24 bins), with the CVaR label | `/api/monte-carlo` → `histogram` |

The static SVG shapes and fixed histogram bars were removed from the HTML. Each chart is now an empty `<svg>` or `<div>` with an id that `terminal.js` fills.

### 2. Backend

- `src/risk/chart_series.py` (new): portfolio value, rebasing, risk thresholds, Monte Carlo fan, histogram, and JSON conversion that maps missing values to `null`.
- `risk_series` uses only past data for each threshold. A test changes a future return and confirms earlier thresholds are unchanged.
- `app.py`: new `POST /api/portfolio/series`. `/api/forecasting/comparison` returns a `series` block aligned on the LSTM test dates. `/api/monte-carlo` returns `fan` and `histogram`.

### 3. Checks

- **Unit tests:** 8 new in `tests/finance_test/test_chart_series.py`. They cover value, rebasing, no look-ahead in the VaR thresholds, the EWMA threshold's breach rate (about 5% on normal returns), fan ordering, histogram totals, and NaN → null. Full suite: **163 passed** (155 + 8).
- **Real-data sanity check:** on the test holdings the EWMA VaR breach rate is **4.69%** over 2,642 scored days. The expected rate is 5%.
- **Wiring audit:** passes. It now also checks chart calls made through `setSvg`.
- **Page-level smoke test** (`terminal.js` in jsdom against the live server): **39 of 39** checks pass. They include chart element counts (3 donut arcs for 2 holdings, 24 histogram bins, 5 volatility models) and a check that no chart coordinate is `NaN` or `Infinity`.

### 4. Not verified

- The smoke test checks that elements exist and have finite coordinates. It does not check how the charts look. I did not view them in a browser, so the layout, colours and label placement still need a visual check.

### 5. Still static (not chart data)

Figures remaining in side panels and commentary: index 47, risk 30, volatility 29, Monte Carlo 27. Examples: the risk page's VaR methodology comparison, the volatility footer metrics (for example "14.2 Sessions", "α+β"), and some Monte Carlo commentary. The README's *Known Limits* lists them.

---

## Session 2 — 2026-10-25 (uploads, dynamic data, wiring, structure)

Request: remove static data, let the user upload the stocks they need and have the
app check them dynamically, check the OCR, check that the frontend is really wired
to the backend, and tidy the file structure.

### 1. What the audit found (before changes)

- **Frontend wiring:** 12 element IDs that `terminal.js` writes to did not exist in
  their pages, so those values never showed. Sidebar "Aggregate Equity ₹14,82,45,900"
  was fixed text on every page.
- **Fabricated values on screen:** overview beta `1.08` and "Beta vs SPY" (no SPY data
  exists), R² `0.91`, "Tilt: Aggressive", Sharpe `2.41`, equity `₹10,00,000`; a fake
  NIFTY 50 level, India VIX, "+2.41% D/D", "v4.18.2 Prod / Latency 4ms" in the header
  and sidebar; a Kite screenshot mock with a fixed `98.42%` confidence and six
  simulated bounding boxes on the Ingestion page.
- **Backend static data:** five hardcoded default holdings (TCS 75, INFY 195, …) were
  the session default; `/api/overview` returned `portfolio_beta: 1.08` and
  `alpha_24h: 0.0121`; `/api/portfolio/ocr` returned `confidence: 0.9842`.
- **OCR:** confidence was fake; the endpoint ran OCR twice per upload; the quantity was
  only read from a fixed screen band (30–45% of width); detected tickers were never
  checked against stored data.
- **Data path:** `data/raw/nse` was resolved relative to the working directory; there was
  no way to add a stock; overlapping files would fail the validator on duplicate dates.
- **Undeclared dependency:** `python-multipart` (needed for uploads) was installed but not
  in `requirements.txt`.

### 2. Updates made

**Backend**

| File | Change |
|---|---|
| `src/data/loader.py` | Data path anchored to the project root. Symbols validated (`A-Z 0-9 & -`, max 20), which blocks path traversal. Column mapping is case- and space-insensitive and covers NSE index headers (`Closing Index Value`, `Index Date`). Rows de-duplicated per date (later uploads win). |
| `src/data/store.py` *(new)* | Lists stored symbols from disk on each call. Validates uploads: needs Date and Close, at least 20 days, positive closes, max 5 MB. Fills the full NSE schema. Saves as `<SYMBOL>_EQ_UPLOAD_*.csv`. ISO dates are read year-first; other dates day-first. |
| `src/finance/beta.py` *(new)* | `cov(p, b) / var(b)` on overlapping dates. Returns `None` with fewer than 30 overlapping days or zero variance. |
| `src/input/ocr.py` | `extract_holdings_detailed()` returns holdings, confidence (mean Tesseract confidence of the words actually used), and raw text, in one OCR pass. Quantity falls back to the first whole number right of the ticker. Duplicate Tesseract setup removed. |
| `app.py` | No default holdings; session starts empty. New `GET /api/symbols` and `POST /api/data/upload`. `/api/portfolio/holdings` values what it can and returns `missing_symbols`. OCR returns real confidence, checks type and size, and returns `missing_symbols`. `/api/overview` (GET and POST) returns beta vs NIFTY50 (null until uploaded) and `last_day_return`; fake beta and alpha removed. Unknown sectors show `UNCLASSIFIED`. Uploads clear the forecast cache. `allow_credentials` set to `False`, since the frontend uses none. |
| `requirements.txt` | Added `python-multipart`. |

**Frontend**

| File | Change |
|---|---|
| `static/terminal.js` | Rewritten. Holdings start empty. Every request uses the server's error message. Upload, OCR and missing-data handlers. Missing values show `—`, never `0`. Values are HTML-escaped. |
| `static/ingestion.html` | Body rebuilt: stock-history upload with the list of stored symbols, OCR panel showing real confidence and raw text, missing-data banner, holdings table, allocation bars, JSON inspector. Mock content removed. |
| `static/index.html` | Beta, Sharpe and equity start as `—` and are filled from the API. Day change bound to `last_day_return`. Fake pills removed. Label now "vs NIFTY 50". |
| `static/risk.html` | Added missing IDs (VaR %, CVaR %, top-contributor %). Hardcoded breakdown rows replaced by a container the script fills. |
| `static/volatility.html` | Added the LSTM T+1 ID. Removed the LSTM training bindings (no element existed). |
| `static/monte_carlo.html` | Added worst-path IDs. Four hardcoded scenario cards replaced by `#scenarios-container`. |
| `static/kinetix.html` | API base is same-origin. It was hardcoded to port 8000. |
| All pages | Fake NIFTY/VIX ticker, "+2.41% D/D" and "Latency 4ms" removed. Sidebar equity is live. |

**Structure**

| From | To |
|---|---|
| `kinetix_full.html` | `static/kinetix.html` (route updated) |
| 6 root scripts (`train_lstm.py`, `run_*.py`, `check_multi_asset.py`, `download_test.py`) | `scripts/` (each gets a path bootstrap so it runs from the root) |
| `oos_volatility_comparison.png` | `outputs/` (script output path updated) |
| `stitch_portfolio_analysis_forecasting_dashboard/` and `.zip` | `design/` |
| `tests/data_pipline/`, `tests/forcasting_test/` | `tests/data_pipeline/`, `tests/forecasting_test/` (typos fixed) |
| `main.py` (empty) | removed (`git rm`) |
| *new* | `scripts/check_frontend_wiring.py` |

Not moved: `data/raw/nse/Quote-Equity-TCS-*.csv` (three tests read these exact paths).

### 3. Tests and checks

- **Unit tests:** 17 new. `test_beta.py` (4), `test_store.py` (11), `test_ocr_confidence.py` (2; skipped when Tesseract is missing). Full suite: **155 passed** (138 existing + 17).
- **Wiring audit:** `python scripts/check_frontend_wiring.py` went from 12 problems to passing. It checks element IDs per page and every API URL against `app.py` routes.
- **Live API checks** (uvicorn, real data):
  - Ticker absent from data → listed in `missing_symbols`.
  - Upload of a generic CSV → stored, valued, and included in the total.
  - Upload of an NIFTY-style index file → accepted; beta computed.
  - `../etc` as a ticker → rejected. CSV without a Close column → rejected with a clear message.
  - OCR on a generated screenshot → `TCS 75, INFY 195, RELIANCE 70` detected with confidence 0.9465 (was a fixed 0.9842).
- **Page-level smoke test:** `terminal.js` run inside jsdom against the live server, 26 checks: overview, ingestion (valuation, missing banner, empty state, no fake ticker), risk, Monte Carlo (4 scenarios), volatility (GARCH and LSTM). **26 of 26 passed.**

### 4. Bugs found while testing (and fixed)

1. **ISO dates swapped day and month.** `2025-06-12` was stored as 6 December. Caused by reading all dates day-first. Fixed with year-first parsing for ISO dates. Regression test added.
2. **Two uploads in the same second overwrote each other.** Fixed by adding microseconds to the stored file name. The override test now exercises the real path.
3. **Own test bugs** (wrong fixtures) corrected: the beta overlap test shifted values, not dates; the schema test expected `SYMBOL` from the wrong function.

### 5. Still open (not done this session)

- **Figures still hardcoded:** index 60, risk 32, volatility 28, Monte Carlo 29. Most are decorative: SVG chart paths, histograms and cones, the model-comparison matrix, and text such as "14.2 Sessions", "α+β 0.852", "2,641 daily obs", "89 of 142 violations", and the "Explainable Risk Intelligence" card. These need new chart-data endpoints or removal. The headline metrics and tables on these pages are now live.
- **Latency:** each valuation tries the NSE live API for every stock first. About 2–4 s for three stocks here. It can be far slower if NSE blocks the request.
- **Stale history:** the bundled NSE files end 2026-09-04, and today is 2026-10-25. The Ingestion page shows each stock's last date.
- **Stress scenario shocks** are fixed numbers in `app.py`. They are scenario definitions, not market data.
- **Single-user state:** holdings and forecast cache are process-wide. No authentication.
- **Line-ending churn** from the earlier session is still unresolved. Nothing is committed.

### 6. Outcome

- Tests: 155 passed. Wiring audit: passes. Page smoke test: 26 of 26.
- Working tree: changes are uncommitted. Review with `git status` before committing.

---

## Session 1 — 2026-10-25

### 1. Project understanding

RiskLens is a FastAPI + static-HTML quantitative risk terminal for NSE equities.

- **Entry points:** `app.py` (main server, 22 routes), `api.py` (alias that re-exports `app`).
- **Frontend:** `static/*.html` + `static/terminal.js`, plus the standalone `kinetix_full.html`.
- **Core packages:**
  - `src/data/` — NSE CSV loading, cleaning, live price lookup with CSV fallback.
  - `src/finance/` — returns, covariance, Euler risk contribution.
  - `src/risk/` — historical / parametric / Monte Carlo VaR and CVaR, dynamic (EWMA) risk, backtesting, scenarios.
  - `src/forecasting/` — Rolling, EWMA, GARCH(1,1), LSTM (PyTorch) volatility models and OOS evaluation.
  - `src/input/` — manual holdings, OCR (Tesseract) screenshot ingestion, verification.
- **Tests:** `tests/` (138 tests, pytest). `pytest.ini` is effectively empty.
- **Python:** 3.12 in `.venv/` (git-ignored).

Every `/api/*` path the frontend calls exists on the server.

### 2. Baseline check (before any change)

- `pytest`: **138 passed** (about 6 min; the LSTM tests are slow).
- `pyflakes` over `app.py`, `api.py`, `src/`, `tests/`: unused imports, unused variables, redefinitions, and f-strings without placeholders.
- The git diff is much larger than the real change because most of it is **CRLF ↔ LF line-ending churn**. Ignoring CR at EOL, the real change is about 12 files.

### 3. Updates made this session

| File | Change |
|---|---|
| `app.py` | Removed unused imports: `List`, `JSONResponse`, `calculate_annualized_ewma_volatility`, `calculate_rolling_volatility_forecast`. |
| `src/forecasting/lstm_model.py` | Removed unused `import torch` (only `torch.nn` is used). |
| `src/input/ocr_engine.py` | Removed unused `import os`. |
| `src/risk/parametric_var.py` | Removed unused `numpy` import and the unused `tail_probability` variable. |
| `src/data/current_prices.py` | **Bug fix:** a symbol whose live NSE fetch failed was never cached, so every request re-hit NSE (up to 2 HTTP calls per symbol, 10 s + 15 s timeouts) before falling back to CSV. Added `_LIVE_MISSES`, reset on the same 60 s TTL as `_LIVE_CACHE`. |

Not committed. All changes are in the working tree.

### 4. Outcome after the changes

- `pytest`: **138 passed** (re-run after the edits).
- `pyflakes` on the edited files: clean.
- `import app`: OK, 22 routes registered.

### 5. Errors found but NOT changed (need a decision)

**High — misleading data shown as real**
1. `app.py` `/api/overview` returns hardcoded `portfolio_beta: 1.08` and `alpha_24h: 0.0121`. `static/index.html` (line ~91, "Portfolio Beta vs SPY") displays `1.08` as a fixed value. Beta is never computed, and the repo has no SPY series.
2. `app.py` `/api/portfolio/ocr` returns a hardcoded `confidence: 0.9842` regardless of OCR quality. `static/ingestion.html` also contains static `0.98` badges.

**Medium — security and robustness**
3. `app.py` CORS: `allow_origins=["*"]` together with `allow_credentials=True`. Fine for local dev, unsafe if deployed.
4. `app.py` `session_state` is one global dict. All users share holdings, and a single OCR upload overwrites them for everyone.
5. `app.py` `_FORECAST_CACHE` grows without bound and is never invalidated. Each uncached `/api/forecasting/comparison` call retrains the LSTM (15 epochs) inside the request.
6. `app.py` `/api/portfolio/current` returns HTTP 200 with `status: "partial"` on error, so clients can't tell a failure from success by status code.
7. `/api/portfolio/ocr` writes OCR-detected holdings into session state without running `validate_holdings`.
8. `app.py` mounts `static/` and reads `static/*.html` and `kinetix_full.html` with paths relative to the current directory. Startup from any other directory breaks these pages.

**Low — code hygiene**
9. `src/input/ocr.py` and `src/input/ocr_engine.py` both contain the same Tesseract path block. In `ocr.py` it sits between import groups (`src.*` imports follow it). Unused imports remain: `pandas`, `extract_text_from_image`, `PortfolioInput`.
10. `src/data/current_prices.py` returns a `"_sources"` metadata key inside the price dict. Every caller must `pop` it, and a missed pop would leak into valuation.
11. `tests/dynamic_engine/test_dynamic_backtesting.py` and `test_dynamic_var_validation.py`: `correlation_matrix` is computed but no longer used, because its argument was removed from `backtest_dynamic_ewma_var`.
12. Other unused imports across `src/` and `tests/` (see `pyflakes` output): `pandas` in about 8 modules, `timedelta` in `downloader.py`, `torch` in `lstm_model` (fixed), duplicate defs in `src/forecasting/evaluation.py`.
13. `main.py` is an empty file. `download_test.py`, `check_multi_asset.py`, `run_*.py`, `train_lstm.py` sit at the root as scratch scripts.
14. `api.py` uses `from app import *`, so names it re-exports are not checkable by static analysis.
15. Line endings: working copy is LF and git expects CRLF, so `app.py` and others show as fully rewritten. Add a `.gitattributes` or normalize once, then commit.

### 6. Suggested next steps

1. Decide on items 1–2: remove the hardcoded values (return `null` / hide the card), or implement beta vs SPY and real OCR confidence.
2. Decide the deployment target, then tighten CORS and move `session_state` to per-user storage (item 3–4).
3. Normalize line endings, then commit the real changes separately from the churn.
4. Clean up the low-priority items as a separate pass.

---

_How to maintain this log: add a new "Session N" section at the top with date, what changed (file + reason), the test/lint results after the change, and any open items. Keep "Outcome" to what was actually run._
