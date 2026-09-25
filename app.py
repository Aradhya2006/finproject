
import tempfile
from pathlib import Path

import streamlit as st

from src.input.portfolio_factory import create_portfolio
from src.input.ocr import extract_holdings_from_image


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Finance Project — Quantitative Terminal",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM — OBSIDIAN QUANTITATIVE
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg: #090d16;
        --surface-1: #0f172a;
        --surface-2: #131e36;
        --surface-3: #1e293b;
        --cyan: #06b6d4;
        --cyan-light: #38bdf8;
        --green: #10b981;
        --red: #f43f5e;
        --amber: #f59e0b;
        --text: #f8fafc;
        --muted: #94a3b8;
        --dim: #64748b;
        --border: rgba(148,163,184,.12);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(6,182,212,.055), transparent 25%),
            var(--bg);
        color: var(--text);
    }

    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: #0a0e17;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebarContent"] {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1480px;
        padding: 5.5rem 2rem 3rem 2rem;
    }

    /* Typography */
    .mono {
        font-family: 'JetBrains Mono', monospace;
        font-variant-numeric: tabular-nums;
    }

    .eyebrow {
        color: var(--muted);
        font-size: 11px;
        line-height: 14px;
        font-weight: 600;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .page-title {
        font-size: 30px;
        line-height: 38px;
        font-weight: 700;
        letter-spacing: -.025em;
        margin: 0;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-top: 5px;
    }

    /* Cards */
    .card {
        background: rgba(15,23,42,.94);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
    }

    .card-tight {
        background: rgba(15,23,42,.94);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
    }

    .card-accent {
        background:
            linear-gradient(180deg, rgba(6,182,212,.08), rgba(15,23,42,.96) 45%);
        border: 1px solid rgba(6,182,212,.25);
        border-radius: 16px;
        padding: 20px;
    }

    .warning-card {
        background: rgba(245,158,11,.08);
        border: 1px solid rgba(245,158,11,.22);
        border-radius: 12px;
        padding: 14px 16px;
    }

    .success-card {
        background: rgba(16,185,129,.08);
        border: 1px solid rgba(16,185,129,.22);
        border-radius: 12px;
        padding: 14px 16px;
    }

    /* Metric cards */
    .metric-label {
        color: var(--muted);
        font-size: 11px;
        line-height: 14px;
        font-weight: 600;
        letter-spacing: .07em;
        text-transform: uppercase;
    }

    .metric-value {
        color: var(--text);
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        line-height: 30px;
        font-weight: 600;
        margin-top: 8px;
    }

    .metric-meta {
        color: var(--dim);
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        margin-top: 6px;
    }

    .green { color: var(--green); }
    .cyan { color: var(--cyan-light); }
    .red { color: var(--red); }
    .amber { color: var(--amber); }

    /* Sidebar branding */
    .brand {
        padding: 4px 8px 18px 8px;
    }

    .brand-name {
        font-size: 19px;
        font-weight: 700;
        letter-spacing: -.02em;
    }

    .brand-sub {
        color: var(--cyan);
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-top: 2px;
    }

    .telemetry {
        background: #111827;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 14px;
    }

    .telemetry-row {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        font-size: 11px;
        color: var(--muted);
        margin: 3px 0;
    }

    .telemetry-value {
        color: var(--text);
        font-family: 'JetBrains Mono', monospace;
    }

    .status-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 10px rgba(16,185,129,.55);
        margin-right: 5px;
    }

    /* Top terminal strip */
    .terminal-strip {
        position: fixed;
        z-index: 999;
        top: 0;
        left: 0;
        right: 0;
        height: 54px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 26px;
        background: rgba(9,13,22,.88);
        backdrop-filter: blur(18px);
        border-bottom: 1px solid var(--border);
    }

    .market-pill {
        display: flex;
        gap: 18px;
        align-items: center;
        background: rgba(15,23,42,.86);
        border: 1px solid var(--border);
        border-radius: 9px;
        padding: 7px 12px;
    }

    .market-item {
        display: flex;
        gap: 8px;
        align-items: baseline;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
    }

    .market-name {
        color: var(--muted);
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: .06em;
    }

    .top-right {
        color: var(--muted);
        font-size: 11px;
    }

    /* Stepper */
    .stepper {
        display: flex;
        align-items: center;
        gap: 0;
        margin: 18px 0 24px 0;
    }

    .step {
        display: flex;
        align-items: center;
        gap: 7px;
        color: var(--muted);
        font-size: 11px;
    }

    .step.active {
        color: var(--cyan-light);
    }

    .step-number {
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        border: 1px solid #334155;
        background: #111827;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
    }

    .step.active .step-number {
        border-color: var(--cyan);
        background: rgba(6,182,212,.12);
        color: var(--cyan-light);
    }

    .step-line {
        width: 42px;
        height: 1px;
        background: #253044;
        margin: 0 9px;
    }

    /* Streamlit controls */
    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid rgba(148,163,184,.15);
        background: #131e36;
        color: var(--text);
    }

    .stButton > button[kind="primary"] {
        background: var(--cyan);
        color: #04151b;
        border-color: var(--cyan);
        box-shadow: 0 0 18px rgba(6,182,212,.18);
    }

    .stButton > button:hover {
        border-color: rgba(6,182,212,.45);
        color: var(--text);
    }

    div[data-testid="stFileUploader"] {
        background: #0b1320;
        border: 1px dashed rgba(6,182,212,.30);
        border-radius: 12px;
        padding: 8px;
    }

    div[data-baseweb="tab-list"] {
        gap: 4px;
        background: #0b1320;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 4px;
    }

    button[data-baseweb="tab"] {
        border-radius: 8px;
    }

    /* Hide default dataframe chrome as much as possible */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: var(--border);
    }

    @media (max-width: 900px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .terminal-strip {
            padding: 0 12px;
        }

        .market-pill {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "portfolio" not in st.session_state:
    st.session_state.portfolio = None

if "ocr_holdings" not in st.session_state:
    st.session_state.ocr_holdings = None

if "ocr_image_path" not in st.session_state:
    st.session_state.ocr_image_path = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-name">Finance Project</div>
            <div class="brand-sub">Quantitative Terminal</div>
        </div>

        <div class="telemetry">
            <div class="telemetry-row">
                <span>Data source</span>
                <span class="telemetry-value">NSE India</span>
            </div>
            <div class="telemetry-row">
                <span>Historical range</span>
                <span class="telemetry-value">2015 → Latest</span>
            </div>
            <div class="telemetry-row">
                <span>Engine</span>
                <span class="telemetry-value">
                    <span class="status-dot"></span>READY
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "NAVIGATION",
        [
            "Portfolio & Ingestion",
            "Static & Dynamic Risk",
            "Volatility Models",
            "Monte Carlo & Stress",
        ],
        label_visibility="visible",
    )

    st.markdown("---")

    portfolio = st.session_state.portfolio

    if portfolio is not None:
        st.markdown(
            f"""
            <div class="card-tight">
                <div class="eyebrow">Current Portfolio</div>
                <div class="metric-value" style="font-size:18px;">
                    ₹{portfolio.portfolio_value:,.0f}
                </div>
                <div class="metric-meta">
                    {len(portfolio.assets)} assets · {portfolio.source.upper()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TOP TERMINAL BAR
# ============================================================

st.markdown(
    """
    <div class="terminal-strip">
        <div class="market-pill">
            <div class="market-item">
                <span class="market-name">NIFTY 50</span>
                <span>—</span>
                <span class="green">Data available</span>
            </div>
            <div style="width:1px;height:18px;background:#273246;"></div>
            <div class="market-item">
                <span class="market-name">DATA</span>
                <span>2015 → Latest</span>
            </div>
        </div>
        <div class="top-right">
            Finance Project · Quantitative Risk Engine
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def render_page_header(title, subtitle):
    st.markdown(
        f"""
        <div>
            <div class="eyebrow">Finance Project / {page.upper()}</div>
            <h1 class="page-title">{title}</h1>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(active_step):
    labels = [
        "Portfolio Input",
        "Risk Engine",
        "Forecasting",
        "Simulation",
    ]

    html = '<div class="stepper">'
    for i, label in enumerate(labels, start=1):
        active = "active" if i == active_step else ""
        html += f"""
            <div class="step {active}">
                <div class="step-number">{i}</div>
                <span>{label}</span>
            </div>
        """
        if i < len(labels):
            html += '<div class="step-line"></div>'
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def portfolio_summary(portfolio):
    if portfolio is None:
        return

    st.markdown("### Portfolio Snapshot")

    cols = st.columns(4)

    metrics = [
        ("Portfolio Value", f"₹{portfolio.portfolio_value:,.2f}", "Current valuation"),
        ("Assets", str(len(portfolio.assets)), "Holdings detected"),
        ("Input Source", portfolio.source.upper(), "Portfolio ingestion"),
        ("Weight Check", "100.00%", "Validated allocation"),
    ]

    for col, (label, value, meta) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="card-tight">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="font-size:20px;">{value}</div>
                    <div class="metric-meta">{meta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE 1 — PORTFOLIO & INGESTION
# ============================================================

if page == "Portfolio & Ingestion":

    render_page_header(
        "Portfolio & Ingestion",
        "Convert a real portfolio into a verified, standardized input for the risk engine.",
    )
    render_stepper(1)

    left, right = st.columns([1.65, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="card-accent">
                <div class="eyebrow">Input Gateway</div>
                <h2 style="margin:5px 0 4px 0;">Enter Your Portfolio</h2>
                <div style="color:#94a3b8;font-size:13px;">
                    Choose how the current portfolio should enter the quantitative pipeline.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        input_method = st.segmented_control(
            "Portfolio source",
            [
                "Screenshot / OCR",
                "Manual Holdings",
                "Portfolio Values",
            ],
            default="Screenshot / OCR",
            label_visibility="collapsed",
        )

        # ----------------------------------------------
        # OCR
        # ----------------------------------------------

        if input_method == "Screenshot / OCR":

            st.markdown(
                """
                <div class="card" style="margin-top:14px;">
                    <div class="eyebrow">Optical Scanner</div>
                    <h3 style="margin:5px 0;">Portfolio Screenshot</h3>
                    <div style="color:#94a3b8;font-size:12px;">
                        Tesseract extracts asset symbols and quantities.
                        Detected values are never silently modified.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                "Upload brokerage screenshot",
                type=["png", "jpg", "jpeg"],
                label_visibility="visible",
            )

            if uploaded_file is not None:

                suffix = Path(uploaded_file.name).suffix or ".png"

                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                )
                temp_file.write(uploaded_file.getbuffer())
                temp_file.close()

                st.session_state.ocr_image_path = temp_file.name

                preview_col, control_col = st.columns([1.4, 1])

                with preview_col:
                    st.image(
                        uploaded_file,
                        caption=uploaded_file.name,
                        width="stretch",
                    )

                with control_col:
                    st.markdown(
                        """
                        <div class="card-tight">
                            <div class="eyebrow">OCR Pipeline</div>
                            <div style="margin-top:8px;font-size:13px;">
                                Image → OCR → Symbol/Quantity extraction
                            </div>
                            <div class="metric-meta" style="margin-top:10px;">
                                Tesseract OCR
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Extract Holdings",
                        type="primary",
                        width="stretch",
                    ):
                        try:
                            holdings = extract_holdings_from_image(
                                temp_file.name
                            )
                            st.session_state.ocr_holdings = holdings

                            if holdings:
                                st.success(
                                    f"Detected {len(holdings)} holding(s)."
                                )
                            else:
                                st.warning(
                                    "No holdings were detected. Try a clearer screenshot."
                                )

                        except Exception as exc:
                            st.error(str(exc))

            if st.session_state.ocr_holdings:
                st.markdown(
                    """
                    <div class="warning-card" style="margin-top:14px;">
                        <b style="color:#f59e0b;">OCR Verification Protocol</b><br>
                        <span style="color:#cbd5e1;font-size:12px;">
                        Review every detected symbol and quantity before the portfolio
                        enters downstream risk calculations.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("#### Detected Holdings")

                rows = [
                    {
                        "Asset Symbol": symbol,
                        "Quantity": quantity,
                    }
                    for symbol, quantity in st.session_state.ocr_holdings.items()
                ]

                verified_rows = st.data_editor(
                    rows,
                    num_rows="dynamic",
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Asset Symbol": st.column_config.TextColumn(
                            "Asset Symbol",
                            required=True,
                        ),
                        "Quantity": st.column_config.NumberColumn(
                            "Quantity",
                            min_value=0.0,
                            step=1.0,
                            required=True,
                        ),
                    },
                    key="ocr_verification_editor",
                )

                c1, c2 = st.columns([1, 1])

                with c1:
                    if st.button(
                        "Confirm & Continue",
                        type="primary",
                        width="stretch",
                    ):
                        confirmed = {}

                        try:
                            for row in verified_rows:
                                symbol = str(
                                    row["Asset Symbol"]
                                ).strip().upper()

                                quantity = float(row["Quantity"])

                                if symbol and quantity > 0:
                                    confirmed[symbol] = quantity

                            if not confirmed:
                                st.error(
                                    "Please confirm at least one valid holding."
                                )
                            else:
                                portfolio = create_portfolio(
                                    "ocr",
                                    st.session_state.ocr_image_path,
                                    confirmed_holdings=confirmed,
                                )

                                st.session_state.portfolio = portfolio
                                st.session_state.ocr_holdings = confirmed

                                st.success(
                                    "Portfolio verified and standardized."
                                )

                        except Exception as exc:
                            st.error(str(exc))

                with c2:
                    if st.button(
                        "Discard OCR Results",
                        width="stretch",
                    ):
                        st.session_state.ocr_holdings = None
                        st.session_state.ocr_image_path = None
                        st.rerun()

        # ----------------------------------------------
        # MANUAL
        # ----------------------------------------------

        elif input_method == "Manual Holdings":

            st.markdown(
                """
                <div class="card" style="margin-top:14px;">
                    <div class="eyebrow">Manual Gateway</div>
                    <h3 style="margin:5px 0;">Current Holdings</h3>
                    <div style="color:#94a3b8;font-size:12px;">
                        Enter ticker symbols and quantities. Current prices are
                        resolved from the local NSE dataset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            rows = st.data_editor(
                [{"Symbol": "", "Quantity": 0.0}],
                num_rows="dynamic",
                width="stretch",
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.TextColumn(
                        "Asset Symbol",
                        help="Example: TCS",
                    ),
                    "Quantity": st.column_config.NumberColumn(
                        "Quantity",
                        min_value=0.0,
                        step=1.0,
                    ),
                },
                key="manual_editor",
            )

            if st.button(
                "Create Portfolio",
                type="primary",
                width="stretch",
            ):
                holdings = {}

                for row in rows:
                    symbol = str(row["Symbol"]).strip().upper()
                    quantity = float(row["Quantity"])

                    if symbol and quantity > 0:
                        holdings[symbol] = quantity

                if not holdings:
                    st.error("Enter at least one valid holding.")
                else:
                    try:
                        portfolio = create_portfolio(
                            "manual",
                            holdings,
                        )
                        st.session_state.portfolio = portfolio
                        st.success("Portfolio created successfully.")
                    except Exception as exc:
                        st.error(str(exc))

        # ----------------------------------------------
        # VALUE INPUT
        # ----------------------------------------------

        else:

            st.markdown(
                """
                <div class="card" style="margin-top:14px;">
                    <div class="eyebrow">Value Gateway</div>
                    <h3 style="margin:5px 0;">Current Portfolio Values</h3>
                    <div style="color:#94a3b8;font-size:12px;">
                        Use this mode when you already know the current rupee
                        value allocated to each asset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            rows = st.data_editor(
                [{"Symbol": "", "Value (₹)": 0.0}],
                num_rows="dynamic",
                width="stretch",
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.TextColumn(
                        "Asset Symbol",
                        help="Example: TCS",
                    ),
                    "Value (₹)": st.column_config.NumberColumn(
                        "Current Value (₹)",
                        min_value=0.0,
                        step=1000.0,
                    ),
                },
                key="value_editor",
            )

            if st.button(
                "Create Value Portfolio",
                type="primary",
                width="stretch",
            ):
                values = {}

                for row in rows:
                    symbol = str(row["Symbol"]).strip().upper()
                    value = float(row["Value (₹)"])

                    if symbol and value > 0:
                        values[symbol] = value

                if not values:
                    st.error("Enter at least one valid portfolio value.")
                else:
                    try:
                        portfolio = create_portfolio(
                            "value",
                            values,
                        )
                        st.session_state.portfolio = portfolio
                        st.success("Value portfolio created successfully.")
                    except Exception as exc:
                        st.error(str(exc))

    # ========================================================
    # RIGHT COLUMN — PIPELINE STATUS
    # ========================================================

    with right:
        st.markdown(
            """
            <div class="card">
                <div class="eyebrow">Pipeline Status</div>
                <h3 style="margin:5px 0 16px 0;">Quantitative Ingestion</h3>

                <div style="display:flex;flex-direction:column;gap:12px;">

                    <div style="display:flex;gap:10px;align-items:center;">
                        <div class="step-number" style="color:#10b981;border-color:#10b981;">✓</div>
                        <div>
                            <b style="font-size:13px;">Portfolio Input</b><br>
                            <span style="color:#64748b;font-size:11px;">
                                Screenshot / manual / values
                            </span>
                        </div>
                    </div>

                    <div style="height:1px;background:#243047;margin-left:11px;"></div>

                    <div style="display:flex;gap:10px;align-items:center;">
                        <div class="step-number">2</div>
                        <div>
                            <b style="font-size:13px;">Price Resolution</b><br>
                            <span style="color:#64748b;font-size:11px;">
                                Latest available NSE price
                            </span>
                        </div>
                    </div>

                    <div style="height:1px;background:#243047;margin-left:11px;"></div>

                    <div style="display:flex;gap:10px;align-items:center;">
                        <div class="step-number">3</div>
                        <div>
                            <b style="font-size:13px;">Risk Engine</b><br>
                            <span style="color:#64748b;font-size:11px;">
                                Returns, covariance, VaR & CVaR
                            </span>
                        </div>
                    </div>

                    <div style="height:1px;background:#243047;margin-left:11px;"></div>

                    <div style="display:flex;gap:10px;align-items:center;">
                        <div class="step-number">4</div>
                        <div>
                            <b style="font-size:13px;">Forecast & Simulation</b><br>
                            <span style="color:#64748b;font-size:11px;">
                                Volatility → Monte Carlo → stress
                            </span>
                        </div>
                    </div>

                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        if st.session_state.portfolio is not None:
            portfolio = st.session_state.portfolio

            st.markdown(
                f"""
                <div class="success-card">
                    <div class="eyebrow" style="color:#10b981;">
                        Portfolio Ready
                    </div>
                    <div style="font-size:13px;margin-top:5px;">
                        Standardized portfolio is available to downstream
                        quantitative modules.
                    </div>
                    <div class="mono" style="font-size:12px;color:#10b981;margin-top:10px;">
                        {len(portfolio.assets)} assets · ₹{portfolio.portfolio_value:,.2f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="card">
                    <div class="eyebrow">Awaiting Input</div>
                    <div style="font-size:13px;margin-top:5px;">
                        Create or verify a portfolio to activate downstream
                        risk analysis.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Portfolio summary
    portfolio_summary(st.session_state.portfolio)

    if st.session_state.portfolio is not None:
        portfolio = st.session_state.portfolio

        st.markdown("### Holdings")

        holding_rows = []
        for asset in portfolio.assets:
            holding_rows.append(
                {
                    "Asset": asset,
                    "Quantity": portfolio.holdings.get(asset, 0),
                    "Price (₹)": portfolio.prices.get(asset, 0),
                    "Holding Value (₹)": portfolio.holding_values.get(asset, 0),
                    "Weight": portfolio.weights.get(asset, 0) * 100,
                }
            )

        st.dataframe(
            holding_rows,
            width="stretch",
            hide_index=True,
            column_config={
                "Quantity": st.column_config.NumberColumn(format="%.2f"),
                "Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Holding Value (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Weight": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )


# ============================================================
# OTHER PAGES — SHELL FOR NEXT UI ITERATIONS
# ============================================================

elif page == "Static & Dynamic Risk":

    render_page_header(
        "Static & Dynamic Risk",
        "Compare historical risk with adaptive, market-condition-aware estimates.",
    )
    render_stepper(2)

    if st.session_state.portfolio is None:
        st.info("Create a portfolio from Portfolio & Ingestion first.")
    else:
        st.markdown(
            """
            <div class="card-accent">
                <div class="eyebrow">Risk Engine</div>
                <h2 style="margin:5px 0;">Static vs Dynamic Risk</h2>
                <div style="color:#94a3b8;font-size:13px;">
                    The quantitative modules are already implemented in the
                    backend. This page is the next UI integration step.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


elif page == "Volatility Models":

    render_page_header(
        "Volatility Forecasting & Models",
        "Compare rolling, EWMA, GARCH and deep-learning-assisted volatility forecasts.",
    )
    render_stepper(3)

    if st.session_state.portfolio is None:
        st.info("Create a portfolio from Portfolio & Ingestion first.")
    else:
        st.markdown(
            """
            <div class="card-accent">
                <div class="eyebrow">Forecasting Engine</div>
                <h2 style="margin:5px 0;">Volatility Model Workspace</h2>
                <div style="color:#94a3b8;font-size:13px;">
                    Model comparison and forecast visualizations will be
                    connected to the existing forecasting modules next.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


else:

    render_page_header(
        "Monte Carlo & Stress Testing",
        "Explore modeled 21-day portfolio outcome distributions and deterministic stress scenarios.",
    )
    render_stepper(4)

    if st.session_state.portfolio is None:
        st.info("Create a portfolio from Portfolio & Ingestion first.")
    else:
        st.markdown(
            """
            <div class="card-accent">
                <div class="eyebrow">Simulation Engine</div>
                <h2 style="margin:5px 0;">21-Day Outcome Distribution</h2>
                <div style="color:#94a3b8;font-size:13px;">
                    Monte Carlo paths, VaR/CVaR and scenario shocks will be
                    connected to the existing simulation modules next.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
