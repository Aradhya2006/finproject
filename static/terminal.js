/**
 * RiskLens Quantitative Terminal — Client API Bridge
 *
 * Connects the dashboard screens with the FastAPI backend. Every figure shown
 * comes from the server. Holdings are kept in localStorage and sent with each
 * request, so the browser and the server always value the same portfolio.
 */

const RiskLens = {
  STORAGE_KEY: "risklens_holdings",
  SYMBOL_PATTERN: /^[A-Z0-9&-]{1,20}$/,
  ALLOCATION_COLORS: [
    "bg-primary", "bg-primary-container", "bg-secondary",
    "bg-secondary-container", "bg-tertiary", "bg-tertiary-container",
  ],

  // ============================================================
  // HOLDINGS STATE
  // ============================================================

  // Holdings chosen in this browser. Empty until the user adds some.
  getHoldings() {
    try {
      const saved = JSON.parse(localStorage.getItem(this.STORAGE_KEY) || "{}");
      if (saved && typeof saved === "object") return saved;
    } catch (e) {
      console.warn("Failed to read holdings from localStorage:", e);
    }
    return {};
  },

  hasHoldings() {
    return Object.keys(this.getHoldings()).length > 0;
  },

  // Save holdings in the browser and in the server session.
  async setHoldings(holdings) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(holdings));
    try {
      await this.postJSON("/api/portfolio/save", { holdings });
    } catch (e) {
      // An empty portfolio is valid; the server rejects it, which is fine.
      console.warn("Session holdings not updated:", e.message);
    }
  },

  // ============================================================
  // HTTP HELPERS
  // ============================================================

  // FastAPI errors look like {"detail": "..."}; show that text to the user.
  async errorMessage(res) {
    try {
      const data = await res.json();
      if (typeof data.detail === "string") return data.detail;
      if (data.detail) return JSON.stringify(data.detail);
    } catch (e) {
      // Body was not JSON; fall through to the status text.
    }
    return res.statusText || `Request failed (HTTP ${res.status})`;
  },

  async getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(await this.errorMessage(res));
    return res.json();
  },

  async postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await this.errorMessage(res));
    return res.json();
  },

  // ============================================================
  // FORMATTING
  // ============================================================

  // Missing values render as an em dash, never as zero.
  isMissing(val) {
    return val === null || val === undefined || Number.isNaN(Number(val));
  },

  // Format amount in Indian Rupees (e.g. ₹10,00,750)
  formatINR(amount, round = true) {
    if (this.isMissing(amount)) return "—";
    const val = round ? Math.round(amount) : Number(amount);
    return "₹" + val.toLocaleString("en-IN");
  },

  // Format a fraction as a percentage (e.g. 17.83%)
  formatPercent(val, decimals = 2, includeSign = false) {
    if (this.isMissing(val)) return "—";
    const sign = includeSign && val > 0 ? "+" : "";
    return sign + (val * 100).toFixed(decimals) + "%";
  },

  // Format a plain number (e.g. 1.08)
  formatDecimal(val, decimals = 2) {
    if (this.isMissing(val)) return "—";
    return Number(val).toFixed(decimals);
  },

  escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, ch => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[ch]);
  },

  setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  },

  // Toast notification helper
  showToast(message, type = "info") {
    let container = document.getElementById("terminal-toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "terminal-toast-container";
      container.className = "fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    const colors = {
      success: "bg-secondary text-surface-container-lowest border-secondary",
      error: "bg-error text-surface-container-lowest border-error",
      info: "bg-surface-container-high text-on-surface border-outline-variant",
    };
    toast.className = `px-4 py-3 rounded-lg shadow-xl font-stat-sm text-sm border flex items-center gap-2 pointer-events-auto transition-all transform duration-300 translate-y-2 opacity-0 ${colors[type] || colors.info}`;
    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.remove("translate-y-2", "opacity-0");
    });

    setTimeout(() => {
      toast.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  // Highlight active sidebar navigation based on pathname
  highlightNavigation() {
    const currentPath = window.location.pathname.replace(/\/$/, "") || "/";
    document.querySelectorAll("aside nav a, header nav a").forEach(link => {
      const href = link.getAttribute("href");
      if (!href) return;
      const linkPath = href.replace(/\/$/, "") || "/";
      if (linkPath === currentPath) {
        link.classList.remove("text-on-surface-variant", "hover:bg-surface-container-high");
        link.classList.add("bg-surface-container-high", "text-primary", "font-medium");
      }
    });
  },

  // Sidebar aggregate equity, shown on every page.
  async loadNavEquity() {
    if (!document.getElementById("nav-equity")) return;
    if (!this.hasHoldings()) return;
    try {
      const data = await this.postJSON("/api/portfolio/holdings", { holdings: this.getHoldings() });
      this.setText("nav-equity", this.formatINR(data.portfolio_value));
    } catch (e) {
      console.warn("Sidebar equity unavailable:", e.message);
    }
  },

  // Initialize page based on route
  init() {
    this.highlightNavigation();
    this.loadNavEquity();
    const path = window.location.pathname;

    if (path === "/overview") {
      this.initOverview();
    } else if (path.startsWith("/ingestion")) {
      this.initIngestion();
    } else if (path.startsWith("/risk")) {
      this.initRisk();
    } else if (path.startsWith("/volatility")) {
      this.initVolatility();
    } else if (path.startsWith("/monte-carlo")) {
      this.initMonteCarlo();
    }
  },

  // Overview donut: one arc and one legend row per holding, weights from the API.
  renderOverviewDonut(rows, total) {
    Charts.setSvg("allocation-donut", Charts.donut(rows));
    this.setText("donut-count", `${rows.length} stocks`);
    this.setText("donut-value", this.formatINR(total));
    this.setText("donut-note", "by current value");

    const legend = document.getElementById("allocation-legend");
    if (!legend) return;
    legend.innerHTML = "";

    rows.forEach((row, i) => {
      const item = document.createElement("div");
      item.className = "flex items-center justify-between p-space-xs rounded-lg hover:bg-surface-container-high transition-colors";

      const left = document.createElement("div");
      left.className = "flex items-center gap-space-sm";
      const dot = document.createElement("span");
      dot.className = "w-3 h-3 rounded-full";
      dot.style.background = Charts.COLORS[i % Charts.COLORS.length];
      const name = document.createElement("span");
      name.className = "font-body-md text-body-md text-on-surface font-medium";
      name.textContent = row.symbol;
      left.append(dot, name);

      const right = document.createElement("div");
      right.className = "text-right";
      const pct = document.createElement("span");
      pct.className = "font-stat-sm text-stat-sm text-on-surface font-bold";
      pct.textContent = this.formatPercent(row.weight, 1);
      const value = document.createElement("span");
      value.className = "font-body-sm text-body-sm text-on-surface-variant ml-space-xs";
      value.textContent = this.formatINR(row.value);
      right.append(pct, value);

      item.append(left, right);
      legend.appendChild(item);
    });
  },

  // Overview equity curve and sparkline, from the holdings' value history.
  async renderOverviewSeries() {
    try {
      const series = await this.postJSON("/api/portfolio/series", { holdings: this.getHoldings() });
      Charts.setSvg("equity-chart", Charts.equity(series));
      Charts.setSvg("overview-sparkline", Charts.sparkline(series.portfolio_value));
    } catch (e) {
      this.showToast("Equity chart: " + e.message, "error");
    }
  },

  // Risk chart: daily returns against the VaR thresholds, with the breach rate.
  async renderRiskSeries() {
    try {
      const series = await this.postJSON("/api/portfolio/series", { holdings: this.getHoldings() });
      Charts.setSvg("risk-chart", Charts.risk(series));
      this.setText("risk-breach-pill", `${series.breach_rate_pct.toFixed(1)}% breaches`);
    } catch (e) {
      this.showToast("Risk chart: " + e.message, "error");
    }
  },

  // Monte Carlo fan chart, outcome histogram, and CVaR label, from the simulation.
  renderMonteCarloCharts(mc) {
    Charts.setSvg("mc-fan-chart", Charts.fan(mc.fan, mc.portfolio_value));
    this.renderHistogram(mc.histogram, mc.var_95.value, mc.cvar_95.value);
    this.setText("mc-cvar-zone-label", `CVaR Zone < ${this.formatPercent(mc.cvar_95.pct)}`);
  },

  // One bar per bin. Bins at or below CVaR are the darkest, bins below VaR are lighter.
  renderHistogram(bins, varValue, cvarValue) {
    const box = document.getElementById("mc-histogram");
    if (!box) return;
    box.innerHTML = "";

    const max = Math.max(...bins.map(b => b.count), 1);
    bins.forEach(bin => {
      const bar = document.createElement("div");
      const tone = bin.high <= cvarValue
        ? "bg-error-container/90"
        : bin.high <= varValue ? "bg-tertiary-container" : "bg-surface-variant";
      bar.className = `w-full ${tone} hover:opacity-90 rounded-t`;
      bar.style.height = `${Math.max(2, (bin.count / max) * 100).toFixed(1)}%`;
      bar.title = `${this.formatINR(bin.low)} to ${this.formatINR(bin.high)}: ${bin.count} paths`;
      box.appendChild(bar);
    });
  },

  // Shown on analysis pages when there is nothing to analyse yet.
  requireHoldings() {
    if (this.hasHoldings()) return true;
    this.showToast("Add holdings on the Ingestion page first.", "info");
    return false;
  },

  // ============================================================
  // 1. OVERVIEW PAGE
  // ============================================================
  async initOverview() {
    if (!this.requireHoldings()) return;

    try {
      const data = await this.postJSON("/api/overview", { holdings: this.getHoldings() });

      this.setText("kpi-equity", this.formatINR(data.portfolio_value));
      document.querySelectorAll(".val-overview-equity").forEach(el => {
        el.textContent = this.formatINR(data.portfolio_value);
      });

      const dayChange = this.formatPercent(data.last_day_return, 2, true);
      document.querySelectorAll(".val-day-change").forEach(el => { el.textContent = dayChange; });
      document.querySelectorAll(".val-day-change-pill").forEach(el => { el.textContent = `${dayChange} Today`; });

      this.setText("kpi-beta", this.formatDecimal(data.portfolio_beta, 2));
      this.setText("kpi-sharpe", this.formatDecimal(data.sharpe_ratio, 2));
      this.setText(
        "kpi-beta-note",
        data.portfolio_beta == null
          ? "Upload NIFTY50 history to compute"
          : `Measured against ${data.benchmark}`
      );
      this.setText("beta-scale-current", `Current (${this.formatDecimal(data.portfolio_beta, 2)})`);
      this.renderOverviewDonut(data.holdings, data.portfolio_value);
      await this.renderOverviewSeries();
    } catch (e) {
      this.showToast("Overview: " + e.message, "error");
    }
  },

  // ============================================================
  // 2. INGESTION: HOLDINGS, OCR, PRICE HISTORY
  // ============================================================
  async initIngestion() {
    this.initModeTabs();
    this.initOcr();
    this.initJsonIngest();
    this.initHistoryUpload();

    const addBtn = document.getElementById("btn-manual-add");
    if (addBtn) addBtn.addEventListener("click", () => this.addManualHolding());
    ["manual-ticker", "manual-quantity"].forEach(id => {
      const input = document.getElementById(id);
      if (input) input.addEventListener("keydown", e => {
        if (e.key === "Enter") this.addManualHolding();
      });
    });

    await this.refreshSymbolStatus();
    await this.fetchAndRenderValuation(this.getHoldings());
  },

  initModeTabs() {
    const tabBtns = document.querySelectorAll(".ingestion-mode-tab");
    const sections = [
      document.getElementById("mode-ocr-section"),
      document.getElementById("mode-manual-section"),
      document.getElementById("mode-json-section"),
    ];

    tabBtns.forEach((btn, idx) => {
      btn.addEventListener("click", () => {
        tabBtns.forEach(b => {
          b.classList.remove("bg-surface-container-high", "text-primary");
          b.classList.add("text-on-surface-variant");
        });
        btn.classList.add("bg-surface-container-high", "text-primary");
        btn.classList.remove("text-on-surface-variant");

        sections.forEach((section, i) => {
          if (section) section.style.display = i === idx ? "flex" : "none";
        });
      });
    });
  },

  // Manual add from the form: validate, save, and show the row in the table.
  async addManualHolding() {
    const tickerEl = document.getElementById("manual-ticker");
    const qtyEl = document.getElementById("manual-quantity");
    const errorEl = document.getElementById("manual-error");
    const showError = message => {
      if (!errorEl) return;
      errorEl.textContent = message;
      errorEl.hidden = !message;
    };

    const sym = (tickerEl ? tickerEl.value : "").trim().toUpperCase();
    const qty = Number(qtyEl ? qtyEl.value : "");

    if (!this.SYMBOL_PATTERN.test(sym)) {
      showError("Enter a ticker: letters, digits, '&' or '-' (max 20).");
      return;
    }
    if (!(qty > 0)) {
      showError("Enter a quantity greater than 0.");
      return;
    }

    showError("");
    const holdings = this.getHoldings();
    holdings[sym] = (holdings[sym] || 0) + qty;
    await this.setHoldings(holdings);
    await this.fetchAndRenderValuation(holdings);

    tickerEl.value = "";
    qtyEl.value = "";
    tickerEl.focus();
    this.showToast(`Added ${qty} shares of ${sym}.`, "success");
  },

  initJsonIngest() {
    const btn = document.getElementById("btn-ingest-json");
    const input = document.getElementById("direct-json-input");
    if (!btn || !input) return;

    btn.addEventListener("click", async () => {
      try {
        const raw = input.value.trim();
        let parsed = {};
        if (raw.startsWith("{")) {
          parsed = JSON.parse(raw);
        } else {
          // "TCS, 10" per line (comma or tab separated)
          raw.split("\n").forEach(line => {
            const parts = line.split(/[,\t]/);
            if (parts.length >= 2) {
              const s = parts[0].trim().toUpperCase();
              const q = parseFloat(parts[1].trim());
              if (s && !isNaN(q) && q > 0) parsed[s] = q;
            }
          });
        }
        if (Object.keys(parsed).length === 0) throw new Error("No valid holdings found.");

        await this.setHoldings(parsed);
        await this.fetchAndRenderValuation(parsed);
        this.showToast("Holdings ingested.", "success");
      } catch (err) {
        this.showToast("Invalid JSON or CSV input: " + err.message, "error");
      }
    });
  },

  initOcr() {
    const fileInput = document.getElementById("ocr-file-input");
    const dropZone = document.getElementById("ocr-drop-zone");
    const selectBtn = document.getElementById("btn-select-file");
    if (!fileInput) return;

    if (selectBtn) selectBtn.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", async (e) => {
      if (e.target.files && e.target.files[0]) {
        await this.uploadOCRFile(e.target.files[0]);
        e.target.value = "";
      }
    });

    if (dropZone) {
      dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("border-primary");
      });
      dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("border-primary");
      });
      dropZone.addEventListener("drop", async (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-primary");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          await this.uploadOCRFile(e.dataTransfer.files[0]);
        }
      });
    }
  },

  async uploadOCRFile(file) {
    this.showToast("Reading screenshot with OCR…", "info");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/portfolio/ocr", { method: "POST", body: formData });
      if (!res.ok) throw new Error(await this.errorMessage(res));
      const data = await res.json();

      this.renderOcrResult(data);
      await this.setHoldings(data.detected_holdings);
      await this.fetchAndRenderValuation(data.detected_holdings);
      await this.refreshSymbolStatus();

      const missing = data.missing_symbols.length;
      this.showToast(
        `Detected ${data.count} holdings at ${(data.confidence * 100).toFixed(1)}% OCR confidence.` +
          (missing ? ` ${missing} need price history.` : " Check the quantities before use."),
        missing ? "info" : "success"
      );
    } catch (err) {
      this.showToast("OCR error: " + err.message, "error");
    }
  },

  renderOcrResult(data) {
    const panel = document.getElementById("ocr-result");
    if (panel) panel.hidden = false;
    this.setText("ocr-confidence", `${(data.confidence * 100).toFixed(1)}%`);
    this.setText("ocr-raw-text", data.raw_text || "");
  },

  // Upload form: ticker + CSV file -> stored price history.
  initHistoryUpload() {
    const btn = document.getElementById("btn-upload-history");
    if (!btn) return;

    btn.addEventListener("click", async () => {
      const symbolInput = document.getElementById("history-symbol");
      const fileInput = document.getElementById("history-file");
      const symbol = symbolInput.value.trim().toUpperCase();
      const file = fileInput.files[0];

      if (!this.SYMBOL_PATTERN.test(symbol)) {
        this.showToast("Enter a ticker (letters, digits, '&' or '-', max 20).", "error");
        return;
      }
      if (!file) {
        this.showToast("Choose a CSV file first.", "error");
        return;
      }

      btn.disabled = true;
      try {
        const formData = new FormData();
        formData.append("symbol", symbol);
        formData.append("file", file);

        const res = await fetch("/api/data/upload", { method: "POST", body: formData });
        if (!res.ok) throw new Error(await this.errorMessage(res));
        const data = await res.json();

        this.showToast(
          `${data.symbol}: stored ${data.stored_rows} days (${data.first_date} to ${data.last_date}).`,
          "success"
        );
        symbolInput.value = "";
        fileInput.value = "";

        await this.refreshSymbolStatus();
        await this.fetchAndRenderValuation(this.getHoldings());
      } catch (err) {
        this.showToast("Upload failed: " + err.message, "error");
      } finally {
        btn.disabled = false;
      }
    });
  },

  // Chips for every stored symbol, read from the server.
  async refreshSymbolStatus() {
    const list = document.getElementById("symbol-status-list");
    if (!list) return;

    try {
      const data = await this.getJSON("/api/symbols");
      const stored = data.symbols.filter(s => s.has_history);

      this.setText(
        "data-status",
        stored.length
          ? `${stored.length} stock${stored.length === 1 ? "" : "s"} with price history`
          : "No price history yet"
      );

      list.innerHTML = "";
      if (stored.length === 0) {
        list.innerHTML = '<span class="font-body-sm text-on-surface-variant">No stored stocks yet. Upload a CSV above.</span>';
        return;
      }

      stored.forEach(s => {
        const chip = document.createElement("span");
        chip.className = "font-stat-sm text-stat-sm px-space-xs py-space-2xs rounded bg-surface-container text-on-surface";
        const isBenchmark = s.symbol === data.benchmark;
        chip.textContent = `${s.symbol}${isBenchmark ? " (benchmark)" : ""} · ${s.rows} days · to ${s.last_date}`;
        list.appendChild(chip);
      });
    } catch (e) {
      list.innerHTML = "";
      this.showToast("Could not load stored symbols: " + e.message, "error");
    }
  },

  // Value the holdings from the server and redraw the table and summary.
  async fetchAndRenderValuation(holdings) {
    if (!holdings || Object.keys(holdings).length === 0) {
      this.renderValuation(null);
      return;
    }

    try {
      const data = await this.postJSON("/api/portfolio/holdings", { holdings });
      this.renderValuation(data, holdings);
    } catch (e) {
      this.renderValuation(null, holdings);
      this.showToast("Valuation failed: " + e.message, "error");
    }
  },

  // Redraw the summary and table. Holdings with no price history are shown
  // in the table too, so a stock you add is never silently dropped.
  renderValuation(data, holdings = {}) {
    const rows = data ? data.rows : [];
    const missing = data ? data.missing_symbols : Object.keys(holdings);

    document.querySelectorAll(".val-portfolio-equity").forEach(el => {
      el.textContent = data ? this.formatINR(data.portfolio_value) : "—";
    });
    document.querySelectorAll(".val-holding-count").forEach(el => {
      el.textContent = data ? `${data.holdings_count} Stocks` : "0 Stocks";
    });
    this.setText("top-weight", rows.length ? this.formatPercent(rows[0].weight) : "—");

    const banner = document.getElementById("missing-symbols-banner");
    if (banner) {
      banner.hidden = missing.length === 0;
      this.setText(
        "missing-symbols-text",
        `${missing.join(", ")} ${missing.length === 1 ? "has no stored price history and is" : "have no stored price history and are"} ` +
          "left out of the valuation. Upload the daily CSV below."
      );
    }

    this.renderHoldingsTable(rows, missing, holdings);
    this.renderAllocation(rows);

    this.setText("portfolio-json-inspector", JSON.stringify({
      source: "VALIDATED_PORTFOLIO",
      total_valuation: data ? data.portfolio_value : 0,
      holdings_count: data ? data.holdings_count : 0,
      missing_symbols: missing,
      holdings: rows.map(r => ({
        ticker: `${r.symbol}.NS`,
        sector: r.sector,
        qty: r.quantity,
        price: r.price,
        value: r.value,
        weight: Number(r.weight.toFixed(4)),
        price_source: r.price_source,
      })),
    }, null, 2));
  },

  renderHoldingsTable(rows, missing, holdings) {
    const tbody = document.getElementById("validation-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";

    // Valued holdings first, then holdings that still need price history.
    const lines = rows.map(row => ({ ...row, hasData: true })).concat(
      missing.map(symbol => ({
        symbol,
        quantity: holdings[symbol],
        sector: "",
        price: null,
        value: null,
        weight: null,
        price_source: null,
        hasData: false,
      }))
    );

    if (lines.length === 0) {
      tbody.innerHTML = `
        <tr><td colspan="6" class="py-space-md px-space-md font-body-sm text-body-sm text-on-surface-variant">
          No holdings yet. Add a stock on the Manual tab, paste a list, or read a screenshot.
        </td></tr>`;
      return;
    }

    lines.forEach(row => {
      const sym = this.escapeHtml(row.symbol);
      const live = row.price_source === "live";
      const tr = document.createElement("tr");
      tr.className = "hover:bg-surface-container/40 transition-colors";
      tr.innerHTML = `
        <td class="py-space-md px-space-md">
          <div class="flex items-center gap-space-xs">
            <span class="font-stat-md text-stat-md text-on-surface font-semibold">${sym}</span>
            <span class="font-label-caps text-label-caps text-on-surface-variant bg-surface-container-high px-space-xs py-space-2xs rounded">${this.escapeHtml(row.sector || "UNCLASSIFIED")}</span>
          </div>
        </td>
        <td class="py-space-md px-space-md">
          <input class="w-24 bg-surface-container text-on-surface font-stat-md text-stat-md px-space-sm py-space-2xs rounded-lg row-qty-input" data-symbol="${sym}" type="number" min="0" step="any" value="${row.quantity}"/>
        </td>
        <td class="py-space-md px-space-md">
          <div class="flex items-center gap-space-xs">
            <span class="font-stat-md text-stat-md text-on-surface">${this.formatINR(row.price, false)}</span>
            <span class="font-label-caps text-label-caps px-space-xs py-space-2xs rounded ${!row.hasData ? "bg-tertiary-container/20 text-tertiary" : live ? "bg-secondary/10 text-secondary" : "bg-surface-container-high text-on-surface-variant"}">${!row.hasData ? "NO DATA" : live ? "LIVE" : "CSV"}</span>
          </div>
        </td>
        <td class="py-space-md px-space-md font-stat-md text-stat-md text-on-surface font-medium">${this.formatINR(row.value)}</td>
        <td class="py-space-md px-space-md">
          <div class="flex items-center gap-space-sm">
            <div class="w-16 h-2 bg-surface-container rounded-full overflow-hidden">
              <div class="h-full bg-primary" style="width: ${row.hasData ? (row.weight * 100).toFixed(1) : 0}%"></div>
            </div>
            <span class="font-stat-sm text-stat-sm text-on-surface font-medium">${this.formatPercent(row.weight)}</span>
          </div>
        </td>
        <td class="py-space-md px-space-md text-right">
          <button class="text-on-surface-variant hover:text-error text-sm row-remove-btn" data-symbol="${sym}" title="Remove">✕</button>
        </td>`;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll(".row-qty-input").forEach(input => {
      input.addEventListener("change", async (e) => {
        const sym = e.target.getAttribute("data-symbol");
        const qty = parseFloat(e.target.value);
        if (isNaN(qty) || qty <= 0) {
          this.showToast(`Quantity for ${sym} must be greater than 0.`, "error");
          return;
        }
        const holdings = this.getHoldings();
        holdings[sym] = qty;
        await this.setHoldings(holdings);
        await this.fetchAndRenderValuation(holdings);
      });
    });

    tbody.querySelectorAll(".row-remove-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const sym = e.target.getAttribute("data-symbol");
        const holdings = this.getHoldings();
        delete holdings[sym];
        await this.setHoldings(holdings);
        await this.fetchAndRenderValuation(holdings);
      });
    });
  },

  renderAllocation(rows) {
    const bar = document.getElementById("allocation-bars");
    const legend = document.getElementById("allocation-legend");
    if (bar) bar.innerHTML = "";
    if (legend) legend.innerHTML = "";

    rows.forEach((row, idx) => {
      if (bar) {
        const seg = document.createElement("div");
        seg.className = `${this.ALLOCATION_COLORS[idx % this.ALLOCATION_COLORS.length]} h-full`;
        seg.style.width = `${(row.weight * 100).toFixed(2)}%`;
        seg.title = `${row.symbol}: ${this.formatPercent(row.weight)}`;
        bar.appendChild(seg);
      }
      if (legend) {
        const item = document.createElement("span");
        item.textContent = `${row.symbol} ${this.formatPercent(row.weight)}`;
        legend.appendChild(item);
      }
    });
  },

  // ============================================================
  // 3. STATIC & DYNAMIC RISK ENGINE
  // ============================================================
  async initRisk() {
    const recalculateBtn = document.getElementById("btn-recalculate-risk");
    if (recalculateBtn) {
      recalculateBtn.addEventListener("click", () => this.fetchAndRenderRisk(true));
    }
    await this.fetchAndRenderRisk(false);
  },

  async fetchAndRenderRisk(showFeedback = false) {
    if (!this.requireHoldings()) return;
    if (showFeedback) this.showToast("Recalculating static vs dynamic risk…", "info");

    try {
      const data = await this.postJSON("/api/portfolio/risk", { holdings: this.getHoldings() });

      this.setText("risk-portfolio-value", this.formatINR(data.portfolio_value));
      this.setText("risk-constituents-count", `${Object.keys(data.weights || {}).length} Equities`);

      this.setText("risk-vol-garch", this.formatPercent(data.annualized_volatility_garch));
      this.setText("risk-vol-static", this.formatPercent(data.annualized_volatility_static));

      this.setText("risk-var-value", this.formatINR(data.historical_var_95_value));
      this.setText("risk-var-pct", this.formatPercent(data.historical_var_95));
      this.setText("risk-param-var-value", this.formatINR(data.parametric_var_95_value));

      this.setText("risk-cvar-value", this.formatINR(data.historical_cvar_95_value));
      this.setText("risk-cvar-pct", this.formatPercent(data.historical_cvar_95));

      if (data.top_contributor) {
        this.setText("risk-top-symbol", data.top_contributor.symbol);
        this.setText("risk-top-drag", this.formatPercent(data.top_contributor.drag, 2, true) + " Drag");
        this.setText("risk-top-pct", `${this.formatPercent(data.top_contributor.risk_pct)} of Risk`);
      }

      const tableBody = document.getElementById("risk-breakdown-table-body");
      if (tableBody && data.contributions) {
        tableBody.innerHTML = "";
        data.contributions.forEach(item => {
          const tr = document.createElement("tr");
          tr.className = "hover:bg-surface-container/40 transition-colors";
          tr.innerHTML = `
            <td class="py-space-sm px-space-md">
              <span class="font-stat-md text-stat-md text-on-surface font-semibold">${this.escapeHtml(item.symbol)}</span>
            </td>
            <td class="py-space-sm px-space-md text-on-surface-variant font-stat-sm text-stat-sm">${this.escapeHtml(item.sector)}</td>
            <td class="py-space-sm px-space-md font-stat-md text-stat-md text-on-surface">${this.formatPercent(item.weight)}</td>
            <td class="py-space-sm px-space-md font-stat-md text-stat-md text-primary font-semibold">${this.formatPercent(item.risk_contribution)}</td>
            <td class="py-space-sm px-space-md text-right font-stat-sm text-stat-sm ${item.drag > 0 ? "text-error" : "text-secondary"}">
              ${this.formatPercent(item.drag, 2, true)}
            </td>`;
          tableBody.appendChild(tr);
        });
      }

      await this.renderRiskSeries();
      if (showFeedback) this.showToast("Risk models updated from stored NSE data.", "success");
    } catch (e) {
      this.showToast("Risk: " + e.message, "error");
    }
  },

  // ============================================================
  // 4. VOLATILITY FORECASTING & MODELS
  // ============================================================
  async initVolatility() {
    await this.fetchAndRenderVolatility();
  },

  async fetchAndRenderVolatility() {
    if (!this.requireHoldings()) return;
    this.showToast("Running volatility models (rolling, EWMA, GARCH, LSTM)…", "info");

    try {
      const data = await this.postJSON("/api/forecasting/comparison", { holdings: this.getHoldings() });

      const updateRow = (modelKey, elPrefix) => {
        const rowData = data[modelKey];
        if (!rowData) return;
        this.setText(`${elPrefix}-mae`, this.isMissing(rowData.mae) ? "—" : (rowData.mae * 100).toFixed(2) + "%");
        this.setText(`${elPrefix}-rmse`, this.isMissing(rowData.rmse) ? "—" : (rowData.rmse * 100).toFixed(2) + "%");
        this.setText(`${elPrefix}-corr`, this.isMissing(rowData.correlation) ? "—" : rowData.correlation.toFixed(3));
      };

      updateRow("rolling", "vol-rolling");
      updateRow("ewma", "vol-ewma");
      updateRow("garch", "vol-garch");
      updateRow("lstm", "vol-lstm");

      if (data.latest_forecast) {
        this.setText("latest-garch-forecast", this.formatPercent(data.latest_forecast.garch_annualized));
        this.setText("latest-lstm-forecast", this.formatPercent(data.latest_forecast.lstm_annualized));
      }

      Charts.setSvg("vol-chart", Charts.volatility(data.series));
      this.showToast("Volatility benchmark updated.", "success");
    } catch (e) {
      this.showToast("Volatility: " + e.message, "error");
    }
  },

  // ============================================================
  // 5. MONTE CARLO & STRESS TESTING
  // ============================================================
  async initMonteCarlo() {
    const rerunBtn = document.getElementById("reRunBtn");
    if (rerunBtn) {
      rerunBtn.addEventListener("click", () => this.fetchAndRenderMonteCarlo(true));
    }
    await this.fetchAndRenderMonteCarlo(false);
  },

  async fetchAndRenderMonteCarlo(showFeedback = false) {
    if (!this.requireHoldings()) return;
    if (showFeedback) this.showToast("Simulating 10,000 Merton jump-diffusion paths…", "info");

    try {
      const holdings = this.getHoldings();
      const mcData = await this.postJSON("/api/monte-carlo", { holdings });

      const updateStripMetric = (key, idVal, idPct) => {
        const item = mcData[key];
        if (!item) return;
        this.setText(idVal, this.formatINR(item.value));
        this.setText(idPct, this.formatPercent(item.pct, 2, true));
      };

      updateStripMetric("expected_mean", "mc-mean-value", "mc-mean-pct");
      updateStripMetric("median", "mc-median-value", "mc-median-pct");
      updateStripMetric("p95_bull_tail", "mc-p95-value", "mc-p95-pct");
      updateStripMetric("var_95", "mc-var-value", "mc-var-pct");
      updateStripMetric("cvar_95", "mc-cvar-value", "mc-cvar-pct");
      updateStripMetric("worst_path", "mc-worst-value", "mc-worst-pct");

      this.renderMonteCarloCharts(mcData);

      const scenData = await this.postJSON("/api/scenarios", { holdings });
      const scenContainer = document.getElementById("scenarios-container");
      if (scenContainer && scenData.scenarios) {
        scenContainer.innerHTML = "";
        scenData.scenarios.forEach(scen => {
          const severe = scen.pct <= -0.15;
          const card = document.createElement("div");
          card.className = "bg-surface-container-low rounded-lg p-space-md flex flex-col gap-space-xs hover:bg-surface-variant/40 transition-colors";
          card.innerHTML = `
            <div class="flex items-start justify-between">
              <div class="flex flex-col">
                <div class="flex items-center gap-space-xs">
                  <span class="font-headline-sm text-body-lg text-on-surface font-semibold">${this.escapeHtml(scen.name)}</span>
                  <span class="font-label-caps text-label-caps px-space-xs py-space-2xs rounded-full ${severe ? "bg-error-container/40 text-error" : "bg-tertiary-container/30 text-tertiary-container"} font-semibold">
                    ${severe ? "Severe Shock" : "Systemic"}
                  </span>
                </div>
                <span class="font-body-sm text-body-sm text-on-surface-variant mt-0.5">${this.escapeHtml(scen.description)}</span>
              </div>
              <div class="text-right">
                <span class="font-stat-md text-stat-md text-error font-semibold">${this.formatPercent(scen.pct, 2, true)}</span>
                <span class="font-stat-sm text-stat-sm text-error block">${this.formatINR(scen.value_change)}</span>
              </div>
            </div>
            <div class="w-full bg-surface-container-highest rounded-full h-1.5 mt-space-xs overflow-hidden">
              <div class="bg-error h-full rounded-full" style="width: ${scen.severity_pct.toFixed(0)}%"></div>
            </div>`;
          scenContainer.appendChild(card);
        });
      }

      if (showFeedback) this.showToast("Monte Carlo simulation complete.", "success");
    } catch (e) {
      this.showToast("Monte Carlo: " + e.message, "error");
    }
  },
};

// Auto-run on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  RiskLens.init();
});
