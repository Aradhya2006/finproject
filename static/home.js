/**
 * User-facing page: pick stocks and shares, then show a plain-language
 * result and charts. Holdings are kept in this browser (localStorage).
 */
(function () {
  "use strict";

  var STORAGE_KEY = "risklens_holdings";
  var SYMBOL_PATTERN = /^[A-Z0-9&-]{1,20}$/;
  var PERIOD_LABELS = {
    "1w": "over the next week",
    "1m": "over the next month",
    "3m": "over the next 3 months",
    "6m": "over the next 6 months",
    "1y": "over the next year",
  };
  var state = { holdings: loadHoldings(), period: loadPeriod(), prices: {}, total: null, timer: null };

  var $ = function (id) { return document.getElementById(id); };

  // ---------- storage ----------

  function loadHoldings() {
    try {
      var saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      return saved && typeof saved === "object" ? saved : {};
    } catch (e) {
      return {};
    }
  }

  function loadPeriod() {
    var saved = localStorage.getItem("risklens_period");
    return PERIOD_LABELS[saved] ? saved : "1m";
  }

  function periodLabel() {
    return PERIOD_LABELS[state.period];
  }

  function saveHoldings() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.holdings));
  }

  // ---------- formatting ----------

  function money(value) {
    if (value == null || isNaN(value)) return "—";
    return "₹" + Math.round(value).toLocaleString("en-IN");
  }

  function percent(value, signed) {
    if (value == null || isNaN(value)) return "—";
    var sign = signed && value > 0 ? "+" : "";
    return sign + value.toFixed(1) + "%";
  }

  function changeOf(value, now) {
    return (value / now - 1) * 100;
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function setText(id, text) {
    var el = $(id);
    if (el) el.textContent = text;
  }

  // ---------- requests ----------

  async function errorMessage(res) {
    try {
      var data = await res.json();
      if (typeof data.detail === "string") return data.detail;
    } catch (e) { /* not JSON */ }
    return "Something went wrong. Please try again.";
  }

  async function getJSON(url) {
    var res = await fetch(url);
    if (!res.ok) throw new Error(await errorMessage(res));
    return res.json();
  }

  async function postJSON(url, body) {
    var res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await errorMessage(res));
    return res.json();
  }

  // ---------- stock list ----------

  async function loadStockChoices() {
    var select = $("stock-select");
    try {
      var data = await getJSON("/api/symbols");
      var stored = data.symbols.filter(function (s) { return s.has_history; });
      stored.forEach(function (s) {
        var option = document.createElement("option");
        option.value = s.symbol;
        option.textContent = s.symbol;
        select.appendChild(option);
      });
      setText("stock-help", stored.length
        ? "Only stocks we have price history for are listed."
        : "No stocks are available yet. Please check back later.");
    } catch (e) {
      setText("stock-help", "Could not load the list of stocks: " + e.message);
    }
  }

  function addStock() {
    var symbol = $("stock-select").value;
    var shares = Number($("stock-qty").value);
    var error = $("add-error");

    if (!symbol) return showError(error, "Choose a stock from the list.");
    if (!SYMBOL_PATTERN.test(symbol)) return showError(error, "That stock name is not valid.");
    if (!(shares > 0)) return showError(error, "Enter the number of shares, more than 0.");

    showError(error, "");
    state.holdings[symbol] = (state.holdings[symbol] || 0) + shares;
    $("stock-select").value = "";
    $("stock-qty").value = "";
    changed();
  }

  function showError(el, message) {
    el.textContent = message;
    el.hidden = !message;
  }

  function changed() {
    saveHoldings();
    clearTimeout(state.timer);
    state.timer = setTimeout(refresh, 250);
  }

  // ---------- table ----------

  function renderTable() {
    var tbody = $("holding-rows");
    var symbols = Object.keys(state.holdings).sort();
    tbody.innerHTML = "";
    $("empty-note").hidden = symbols.length > 0;

    symbols.forEach(function (symbol) {
      var price = state.prices[symbol];
      var shares = state.holdings[symbol];
      var value = price ? price.value : null;

      var tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + escapeHtml(symbol) + "</td>" +
        '<td class="num"><input class="shares" type="number" min="0" step="any" value="' + shares + '" aria-label="Shares of ' + escapeHtml(symbol) + '"/></td>' +
        '<td class="num">' + (price ? money(price.price) : "—") + "</td>" +
        '<td class="num">' + money(value) + "</td>" +
        '<td class="num"><button class="quiet" type="button" aria-label="Remove ' + escapeHtml(symbol) + '">Remove</button></td>';

      tr.querySelector("input").addEventListener("change", function (e) {
        var qty = Number(e.target.value);
        if (!(qty > 0)) {
          e.target.value = shares;
          return;
        }
        state.holdings[symbol] = qty;
        changed();
      });

      tr.querySelector("button").addEventListener("click", function () {
        delete state.holdings[symbol];
        changed();
      });

      tbody.appendChild(tr);
    });
  }

  // ---------- result ----------

  async function refresh() {
    var symbols = Object.keys(state.holdings);

    if (symbols.length === 0) {
      state.prices = {};
      state.total = null;
      setText("total-now", "—");
      renderTable();
      $("result-card").hidden = true;
      return;
    }

    try {
      var valuation = await postJSON("/api/portfolio/holdings", { holdings: state.holdings });
      state.prices = {};
      valuation.rows.forEach(function (row) {
        state.prices[row.symbol] = { price: row.price, value: row.value };
      });
      state.total = valuation.portfolio_value;
      setText("total-now", money(state.total));
      renderTable();
    } catch (e) {
      renderTable();
      showError($("result-error"), "We could not value your stocks: " + e.message);
      $("result-card").hidden = false;
      return;
    }

    await renderResult();
  }

  async function renderResult() {
    var card = $("result-card");
    var error = $("result-error");
    card.hidden = false;
    showError(error, "");

    try {
      var result = await postJSON("/api/my-portfolio", { holdings: state.holdings, period: state.period });
      var now = result.value_now;

      var chance = result.chance_of_gain_pct;
      setText("result-title", "2. Your result " + periodLabel());
      setText("paths-title", "Possible paths " + periodLabel());
      setText("headline", chance >= 50
        ? "Your portfolio of " + money(now) + " is more likely to grow than shrink " + periodLabel() + "."
        : "Your portfolio of " + money(now) + " is more likely to fall than grow " + periodLabel() + ".");

      var average = result.average_outcome;
      setText("avg-value", money(average.value));
      setText("avg-change", percent(average.change_pct, true) + " from today");
      $("avg-value").className = "big " + (average.change_pct >= 0 ? "good" : "bad");

      setText("chance", Math.round(chance) + "%");

      var wide = result.wide_range;
      setText("wide-range", money(wide.low) + " to " + money(wide.high));
      setText("wide-change", percent(changeOf(wide.low, now), true) + " to " + percent(changeOf(wide.high, now), true));

      var worst = result.worst_case;
      setText("worst", money(worst.value));
      setText("worst-change", percent(worst.change_pct, true) + " from today");

      Charts.setSvg("fan-chart", Charts.fan(result.paths, now));
      Charts.setSvg("past-chart", Charts.equity({
        dates: result.past.dates,
        portfolio_value: result.past.values,
        benchmark_value: null,
        benchmark: null,
      }));
    } catch (e) {
      showError(error, friendlyError(e.message));
    }
  }

  function friendlyError(message) {
    var missing = /No price history for ([^.]+)\./.exec(message);
    if (missing) {
      return "We do not have price history for " + missing[1] +
        " yet. Remove it from your list to see your result.";
    }
    return "We could not calculate your result: " + message;
  }

  // ---------- start ----------

  document.addEventListener("DOMContentLoaded", function () {
    $("add-stock").addEventListener("click", addStock);
    $("stock-qty").addEventListener("keydown", function (e) {
      if (e.key === "Enter") addStock();
    });
    document.querySelectorAll(".period").forEach(function (button) {
      var active = button.getAttribute("data-period") === state.period;
      button.setAttribute("aria-pressed", active ? "true" : "false");
      button.addEventListener("click", function () {
        state.period = button.getAttribute("data-period");
        localStorage.setItem("risklens_period", state.period);
        document.querySelectorAll(".period").forEach(function (b) {
          b.setAttribute("aria-pressed", b === button ? "true" : "false");
        });
        renderResult();
      });
    });
    loadStockChoices();
    refresh();
  });
})();
