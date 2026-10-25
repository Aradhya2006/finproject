/**
 * RiskLens chart drawing. Each function turns API series into SVG markup.
 * Loaded before terminal.js and home.js.
 */

// ============================================================
// CHARTS: SVG drawn from the series the API returns. Each function
// returns markup for the chart's <svg>; nothing is drawn from fixed numbers.
// ============================================================
const Charts = {
  COLORS: ["#4cd7f6", "#4edea3", "#acedff", "#ffb2b7", "#869397", "#dfe2ef"],
  MONO: 'font-family="JetBrains Mono"',

  // Indian-rupee label for chart axes and ends.
  money(value) {
    return "₹" + Math.round(value).toLocaleString("en-IN");
  },

  // Linear map from domain [d0, d1] onto range [r0, r1].
  scale(d0, d1, r0, r1) {
    const span = d1 - d0 || 1;
    return v => r0 + ((v - d0) / span) * (r1 - r0);
  },

  // [min, max] of the non-missing values.
  range(values) {
    const clean = values.filter(v => v != null);
    return [Math.min(...clean), Math.max(...clean)];
  },

  // SVG path through points; a null point lifts the pen, leaving a gap.
  path(points) {
    let d = "";
    let down = false;
    points.forEach(p => {
      if (p == null) { down = false; return; }
      d += (down ? " L " : " M ") + p[0].toFixed(1) + " " + p[1].toFixed(1);
      down = true;
    });
    return d.trim();
  },

  line(d, color, width = 1.5, dash = "") {
    if (!d) return "";
    return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linejoin="round" stroke-linecap="round"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
  },

  // Put markup into a chart's <svg>. Returns false if the page has no such chart.
  setSvg(id, markup) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = markup;
    return !!el;
  },

  // Holdings value over time, with the benchmark rebased to the same start.
  equity(data) {
    const W = 850, H = 360, top = 20, bottom = H - 30;
    const values = data.portfolio_value;
    if (!values.some(v => v != null)) return "";

    const all = values.concat(data.benchmark_value || []).filter(v => v != null);
    const [lo, hi] = this.range(all);
    const pad = (hi - lo) * 0.08 || hi * 0.02;
    const y = this.scale(lo - pad, hi + pad, bottom, top);
    const x = i => (i / Math.max(values.length - 1, 1)) * W;

    const points = values.map((v, i) => (v == null ? null : [x(i), y(v)]));
    const drawn = points.filter(p => p);
    const first = drawn[0];
    const last = drawn[drawn.length - 1];
    const area = this.path(points) + ` L ${last[0].toFixed(1)} ${bottom} L ${first[0].toFixed(1)} ${bottom} Z`;

    let svg = `<defs><linearGradient id="equity-area" x1="0" x2="0" y1="0" y2="1">` +
      `<stop offset="0" stop-color="#4cd7f6" stop-opacity="0.25"/>` +
      `<stop offset="1" stop-color="#4cd7f6" stop-opacity="0"/></linearGradient></defs>`;

    for (let k = 0; k <= 3; k++) {
      const v = lo - pad + ((hi + pad) - (lo - pad)) * k / 3;
      const yy = y(v).toFixed(1);
      svg += `<line x1="0" x2="${W}" y1="${yy}" y2="${yy}" stroke="#31353f" stroke-dasharray="4 4" stroke-opacity="0.4"/>` +
        `<text x="${W - 6}" y="${yy - 4}" fill="#869397" font-size="11" text-anchor="end" ${this.MONO}>${Charts.money(v)}</text>`;
    }

    svg += `<path d="${area}" fill="url(#equity-area)"/>`;
    if (data.benchmark_value) {
      svg += this.line(this.path(data.benchmark_value.map((v, i) => (v == null ? null : [x(i), y(v)]))), "#869397", 1.5, "4 4");
      svg += `<text x="10" y="16" fill="#869397" font-size="11" ${this.MONO}>Dashed: ${data.benchmark} rebased</text>`;
    }
    svg += this.line(this.path(points), "#4cd7f6", 2.5);
    svg += `<circle cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="5" fill="#4cd7f6" stroke="#0a0e17" stroke-width="2"/>`;
    svg += `<text x="0" y="${H - 8}" fill="#869397" font-size="11" ${this.MONO}>${data.dates[0]}</text>`;
    svg += `<text x="${W}" y="${H - 8}" fill="#869397" font-size="11" text-anchor="end" ${this.MONO}>${data.dates[data.dates.length - 1]}</text>`;
    return svg;
  },

  // Allocation ring: one arc per holding, starting at 12 o'clock.
  donut(rows) {
    const C = 2 * Math.PI * 64;
    let svg = `<circle cx="80" cy="80" r="64" fill="transparent" stroke="#262a34" stroke-width="16"/>`;
    let used = 0;
    rows.forEach((row, i) => {
      const len = row.weight * C;
      svg += `<circle cx="80" cy="80" r="64" fill="transparent" stroke="${this.COLORS[i % this.COLORS.length]}" stroke-width="16" ` +
        `stroke-dasharray="${len.toFixed(2)} ${C.toFixed(2)}" stroke-dashoffset="${(-used).toFixed(2)}"/>`;
      used += len;
    });
    return svg;
  },

  // Last 20 values as a small trend line.
  sparkline(values) {
    const v = values.filter(x => x != null).slice(-20);
    if (v.length < 2) return "";
    const [lo, hi] = this.range(v);
    const y = this.scale(lo, hi, 22, 2);
    const points = v.map((p, i) => [(i / (v.length - 1)) * 80, y(p)]);
    const last = points[points.length - 1];
    return `<path d="${this.path(points)}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>` +
      `<circle cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="2.5" fill="currentColor"/>`;
  },

  // Daily returns with the EWMA and historical 95% VaR thresholds. Breaches are marked.
  risk(data) {
    const W = 700, H = 190, top = 12, bottom = H - 14;
    const returns = data.daily_returns;
    const n = returns.length;
    if (!n) return "";

    const all = returns.concat(data.var_ewma, data.var_historical).filter(v => v != null);
    const lo = Math.min(...all);
    const hi = Math.max(0, ...all);
    const y = this.scale(lo, hi, bottom, top);
    const x = i => (i / Math.max(n - 1, 1)) * W;
    const pts = arr => arr.map((v, i) => (v == null ? null : [x(i), y(v)]));

    let svg = `<line x1="0" x2="${W}" y1="${y(0).toFixed(1)}" y2="${y(0).toFixed(1)}" stroke="#31353f" stroke-dasharray="3 3"/>`;
    svg += this.line(this.path(pts(returns)), "#869397", 1);
    svg += this.line(this.path(pts(data.var_historical)), "#ffb2b7", 1.2, "5 3");
    svg += this.line(this.path(pts(data.var_ewma)), "#4cd7f6", 1.8);

    data.breaches.forEach((breached, i) => {
      if (breached) {
        svg += `<circle cx="${x(i).toFixed(1)}" cy="${y(returns[i]).toFixed(1)}" r="2.5" fill="#ffb4ab"/>`;
      }
    });

    svg += `<text x="8" y="16" fill="#4cd7f6" font-size="11" ${this.MONO}>95% EWMA VaR</text>`;
    svg += `<text x="128" y="16" fill="#ffb2b7" font-size="11" ${this.MONO}>252-day historical</text>`;
    return svg;
  },

  // Annualised volatility: realised against each model, over the same test dates.
  volatility(series) {
    const W = 700, H = 240, top = 34, bottom = H - 22;
    const n = series.dates.length;
    if (!n) return "";

    const models = [
      ["realized", "REALIZED", "#dfe2ef", 1.5, "4 3"],
      ["rolling", "ROLLING", "#869397", 1.5, ""],
      ["ewma", "EWMA", "#acedff", 1.5, ""],
      ["garch", "GARCH", "#4edea3", 1.8, ""],
      ["lstm", "LSTM", "#4cd7f6", 2.2, ""],
    ];

    const all = models.flatMap(([key]) => series[key]).filter(v => v != null);
    if (!all.length) return "";

    const [lo, hi] = this.range(all);
    const pad = (hi - lo) * 0.06 || hi * 0.05;
    const bottomValue = lo - pad;
    const topValue = hi + pad;
    const y = this.scale(bottomValue, topValue, bottom, top);
    const x = i => (i / Math.max(n - 1, 1)) * W;

    let svg = "";
    for (let k = 0; k <= 3; k++) {
      const v = bottomValue + (topValue - bottomValue) * k / 3;
      const yy = y(v).toFixed(1);
      svg += `<line x1="0" x2="${W}" y1="${yy}" y2="${yy}" stroke="#31353f" stroke-dasharray="4 4"/>` +
        `<text x="${W - 4}" y="${yy - 4}" fill="#869397" font-size="10" text-anchor="end" ${this.MONO}>${(v * 100).toFixed(1)}%</text>`;
    }

    models.forEach(([key, label, color, width, dash], idx) => {
      const pts = series[key].map((v, i) => (v == null ? null : [x(i), y(v)]));
      svg += this.line(this.path(pts), color, width, dash);
      svg += `<text x="${8 + idx * 120}" y="16" fill="${color}" font-size="11" ${this.MONO}>— ${label}</text>`;
    });

    svg += `<text x="0" y="${H - 4}" fill="#869397" font-size="10" ${this.MONO}>${series.dates[0]}</text>`;
    svg += `<text x="${W}" y="${H - 4}" fill="#869397" font-size="10" text-anchor="end" ${this.MONO}>${series.dates[n - 1]}</text>`;
    return svg;
  },

  // 21-day outcome fan: 5-95% and 25-75% bands, with the median and tails.
  fan(fan, start) {
    const W = 800, H = 320, top = 14, bottom = H - 22;
    const n = fan.days.length;
    const x = i => (i / Math.max(n - 1, 1)) * W;

    const lo = Math.min(...fan.p05, start);
    const hi = Math.max(...fan.p95, start);
    const pad = (hi - lo) * 0.05;
    const y = this.scale(lo - pad, hi + pad, bottom, top);

    const pts = arr => arr.map((v, i) => [x(i), y(v)]);
    const band = (upper, lower) => this.path(pts(upper).concat(pts(lower).reverse())) + " Z";

    let svg = `<line x1="0" x2="${W}" y1="${y(start).toFixed(1)}" y2="${y(start).toFixed(1)}" stroke="#31353f" stroke-dasharray="4 4"/>`;
    svg += `<path d="${band(fan.p95, fan.p05)}" fill="#4cd7f6" fill-opacity="0.08"/>`;
    svg += `<path d="${band(fan.p75, fan.p25)}" fill="#4cd7f6" fill-opacity="0.16"/>`;
    svg += this.line(this.path(pts(fan.p95)), "#4edea3", 2);
    svg += this.line(this.path(pts(fan.p05)), "#ffb4ab", 2);
    svg += this.line(this.path(pts(fan.p50)), "#dfe2ef", 2.5, "6 3");

    [["p95", "#4edea3"], ["p50", "#dfe2ef"], ["p05", "#ffb4ab"]].forEach(([key, color]) => {
      const v = fan[key][n - 1];
      svg += `<text x="${W - 6}" y="${(y(v) - 6).toFixed(1)}" fill="${color}" font-size="11" text-anchor="end" ${this.MONO}>${Charts.money(v)}</text>`;
    });

    svg += `<text x="0" y="${H - 6}" fill="#869397" font-size="10" ${this.MONO}>Today</text>`;
    svg += `<text x="${W}" y="${H - 6}" fill="#869397" font-size="10" text-anchor="end" ${this.MONO}>Day ${n - 1}</text>`;
    return svg;
  },
};
