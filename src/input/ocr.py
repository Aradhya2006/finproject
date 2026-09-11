import re

from src.data.current_prices import get_latest_prices
from src.input.manual import calculate_portfolio_from_holdings
from src.input.ocr_engine import extract_text_from_image
from src.input.verification import verify_holdings
from src.input.portfolio_input import PortfolioInput


def normalize_symbol(symbol):
    """
    Normalize a stock symbol.
    """
    if not isinstance(symbol, str):
        raise ValueError(
            "Symbol must be a string."
        )

    symbol = symbol.strip().upper()

    if not symbol:
        raise ValueError(
            "Symbol cannot be empty."
        )

    return symbol


def extract_holdings_from_text(text):
    """
    Extract stock symbols and quantities from OCR text.

    Expected examples:
        TCS 10
        INFY 15
        RELIANCE 5

    Returns
    -------
    dict
        Symbol -> quantity
    """
    if not isinstance(text, str):
        raise ValueError(
            "OCR text must be a string."
        )

    if not text.strip():
        raise ValueError(
            "OCR text cannot be empty."
        )

    holdings = {}
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        match = re.search(
            r"\b([A-Za-z][A-Za-z0-9&.-]{1,19})\b"
            r"\s+"
            r"(\d+(?:\.\d+)?)"
            r"\b",
            line,
        )

        if not match:
            continue

        symbol = normalize_symbol(
            match.group(1)
        )

        quantity = float(
            match.group(2)
        )

        if quantity <= 0:
            continue

        holdings[symbol] = (
            holdings.get(symbol, 0.0)
            + quantity
        )

    if not holdings:
        raise ValueError(
            "No holdings could be extracted from OCR text."
        )

    return holdings


def extract_holdings_from_image(image_path):
    """
    Extract portfolio holdings from an image.

    Returns
    -------
    dict
        Symbol -> quantity
    """
    text = extract_text_from_image(
        image_path
    )

    return extract_holdings_from_text(
        text
    )


def create_current_ocr_portfolio(
    image_path,
    confirmed_holdings=None,
):
    """
    Create a current portfolio from a screenshot.

    OCR extracts the initial holdings. The caller can
    optionally provide user-confirmed or edited holdings.
    """

    detected_holdings = extract_holdings_from_image(
        image_path
    )

    verified_holdings = verify_holdings(
        detected_holdings,
        confirmed_holdings,
    )

    prices = get_latest_prices(
        list(verified_holdings.keys())
    )

    portfolio = calculate_portfolio_from_holdings(
        verified_holdings,
        prices,
    )

    portfolio.detected_holdings = detected_holdings
    portfolio.verified_holdings = verified_holdings

    return portfolio