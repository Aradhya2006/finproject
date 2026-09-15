import tempfile

import streamlit as st

from src.input.portfolio_factory import create_portfolio
from src.input.ocr import extract_holdings_from_image


st.set_page_config(
    page_title="Finance Project",
    page_icon="📊",
    layout="wide",
)


st.title("Portfolio Risk Analysis & Volatility Forecasting")

st.write(
    "Analyze your portfolio using historical risk, dynamic volatility "
    "forecasting, Monte Carlo simulation, and stress scenarios."
)

st.divider()

st.header("Enter Your Portfolio")

input_method = st.radio(
    "How would you like to provide your portfolio?",
    [
        "Manual Holdings",
        "Upload Portfolio Screenshot",
        "Portfolio Values",
    ],
    horizontal=True,
)

st.divider()


# =========================================================
# MANUAL HOLDINGS
# =========================================================

if input_method == "Manual Holdings":

    st.subheader("Manual Holdings")

    st.write(
        "Enter the assets you currently hold and the number of shares."
    )

    default_data = [
        {"Symbol": "", "Quantity": 0.0},
    ]

    edited_data = st.data_editor(
        default_data,
        num_rows="dynamic",
        width="stretch",
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
    )

    if st.button("Continue", type="primary"):

        holdings = {}

        for row in edited_data:

            symbol = row["Symbol"].strip().upper()
            quantity = row["Quantity"]

            if symbol:
                holdings[symbol] = quantity

        if not holdings:

            st.error("Please enter at least one asset.")

        else:

            try:

                portfolio = create_portfolio(
                    "manual",
                    holdings,
                )

                st.session_state["portfolio"] = portfolio

                st.success("Portfolio created successfully.")

                st.subheader("Portfolio Summary")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Portfolio Value",
                        f"₹{portfolio.portfolio_value:,.2f}",
                    )

                with col2:

                    st.metric(
                        "Number of Assets",
                        len(portfolio.assets),
                    )

                st.dataframe(
                    {
                        "Asset": portfolio.assets,
                        "Quantity": [
                            portfolio.holdings[a]
                            for a in portfolio.assets
                        ],
                        "Price": [
                            portfolio.prices[a]
                            for a in portfolio.assets
                        ],
                        "Holding Value": [
                            portfolio.holding_values[a]
                            for a in portfolio.assets
                        ],
                        "Weight": [
                            f"{portfolio.weights[a] * 100:.2f}%"
                            for a in portfolio.assets
                        ],
                    },
                    width="stretch",
                )

            except Exception as exc:

                st.error(str(exc))


# =========================================================
# OCR PORTFOLIO
# =========================================================

elif input_method == "Upload Portfolio Screenshot":

    st.subheader("Upload Portfolio Screenshot")

    st.write(
        "Upload a screenshot of your holdings. "
        "The system will extract asset symbols and quantities "
        "using OCR."
    )

    uploaded_file = st.file_uploader(
        "Choose a screenshot",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="Uploaded Portfolio Screenshot",
            width="stretch",
        )

        if st.button(
            "Extract Holdings",
            type="primary",
        ):

            try:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png",
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getvalue()
                    )

                    image_path = temp_file.name

                st.session_state["ocr_image_path"] = image_path

                detected_holdings = (
                    extract_holdings_from_image(
                        image_path
                    )
                )

                if not detected_holdings:

                    st.error(
                        "No holdings could be detected. "
                        "Try a clearer screenshot."
                    )

                else:

                    st.session_state[
                        "detected_holdings"
                    ] = detected_holdings

            except Exception as exc:

                st.error(
                    f"OCR failed: {exc}"
                )


    # -----------------------------------------------------
    # OCR VERIFICATION
    # -----------------------------------------------------

    if "detected_holdings" in st.session_state:

        detected_holdings = (
            st.session_state["detected_holdings"]
        )

        st.divider()

        st.subheader("Verify Detected Holdings")

        st.warning(
            "Please verify the OCR results before continuing. "
            "The system will not silently modify detected values."
        )

        st.write("Detected holdings:")

        verification_data = [
            {
                "Asset Symbol": symbol,
                "Quantity": quantity,
            }
            for symbol, quantity
            in detected_holdings.items()
        ]

        edited_data = st.data_editor(
            verification_data,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "Asset Symbol": st.column_config.TextColumn(
                    "Asset Symbol"
                ),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    min_value=0.0,
                    step=1.0,
                ),
            },
            key="ocr_verification_editor",
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Confirm & Continue",
                type="primary",
            ):

                confirmed_holdings = {}

                for row in edited_data:

                    symbol = (
                        row["Asset Symbol"]
                        .strip()
                        .upper()
                    )

                    quantity = row["Quantity"]

                    if symbol and quantity > 0:

                        confirmed_holdings[
                            symbol
                        ] = quantity

                if not confirmed_holdings:

                    st.error(
                        "Please confirm at least one valid holding."
                    )

                else:

                    try:

                        image_path = (
                            st.session_state.get(
                                "ocr_image_path"
                            )
                        )

                        if not image_path:

                            st.error(
                                "OCR image is no longer available. "
                                "Please upload again."
                            )

                            st.stop()

                        portfolio = create_portfolio(
                            "ocr",
                            image_path,
                            confirmed_holdings=(
                                confirmed_holdings
                            ),
                        )

                        st.session_state[
                            "portfolio"
                        ] = portfolio

                        st.success(
                            "Portfolio verified successfully."
                        )

                        st.subheader(
                            "Portfolio Summary"
                        )

                        col_a, col_b = st.columns(2)

                        with col_a:

                            st.metric(
                                "Portfolio Value",
                                f"₹{portfolio.portfolio_value:,.2f}",
                            )

                        with col_b:

                            st.metric(
                                "Number of Assets",
                                len(portfolio.assets),
                            )

                        st.dataframe(
                            {
                                "Asset": portfolio.assets,
                                "Quantity": [
                                    portfolio.holdings[a]
                                    for a in portfolio.assets
                                ],
                                "Price": [
                                    portfolio.prices[a]
                                    for a in portfolio.assets
                                ],
                                "Holding Value": [
                                    portfolio.holding_values[a]
                                    for a in portfolio.assets
                                ],
                                "Weight": [
                                    f"{portfolio.weights[a] * 100:.2f}%"
                                    for a in portfolio.assets
                                ],
                            },
                            width="stretch",
                        )

                    except Exception as exc:

                        st.error(str(exc))

        with col2:

            if st.button(
                "Discard OCR Results"
            ):

                st.session_state.pop(
                    "detected_holdings",
                    None,
                )

                st.session_state.pop(
                    "ocr_image_path",
                    None,
                )

                st.rerun()


# =========================================================
# PORTFOLIO VALUES
# =========================================================

elif input_method == "Portfolio Values":

    st.subheader("Portfolio Values")

    st.write(
        "Enter the current value of each asset in your portfolio."
    )

    default_data = [
        {"Symbol": "", "Value": 0.0},
    ]

    edited_data = st.data_editor(
        default_data,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Symbol": st.column_config.TextColumn(
                "Asset Symbol",
                help="Example: TCS",
            ),
            "Value": st.column_config.NumberColumn(
                "Current Value (₹)",
                min_value=0.0,
                step=1000.0,
            ),
        },
    )

    if st.button(
        "Continue",
        type="primary",
    ):

        values = {}

        for row in edited_data:

            symbol = (
                row["Symbol"]
                .strip()
                .upper()
            )

            value = row["Value"]

            if symbol:
                values[symbol] = value

        if not values:

            st.error(
                "Please enter at least one asset."
            )

        else:

            try:

                portfolio = create_portfolio(
                    "value",
                    values,
                )

                st.session_state[
                    "portfolio"
                ] = portfolio

                st.success(
                    "Portfolio created successfully."
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Portfolio Value",
                        f"₹{portfolio.portfolio_value:,.2f}",
                    )

                with col2:

                    st.metric(
                        "Number of Assets",
                        len(portfolio.assets),
                    )

                st.dataframe(
                    {
                        "Asset": portfolio.assets,
                        "Value": [
                            portfolio.holding_values[a]
                            for a in portfolio.assets
                        ],
                        "Weight": [
                            f"{portfolio.weights[a] * 100:.2f}%"
                            for a in portfolio.assets
                        ],
                    },
                    width="stretch",
                )

            except Exception as exc:

                st.error(str(exc))