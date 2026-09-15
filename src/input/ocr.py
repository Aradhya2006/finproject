import re

import re

import pandas as pd
import pytesseract
from PIL import Image
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
    Extract holdings from OCR/plain text.

    Expected examples:
        TCS 10
        INFY 15
        RELIANCE 5
    """

    if not isinstance(text, str):
        raise ValueError("OCR text must be a string.")

    if not text.strip():
        raise ValueError("OCR text cannot be empty.")

    holdings = {}

    for line in text.splitlines():

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

        symbol = normalize_symbol(match.group(1))
        quantity = float(match.group(2))

        if quantity <= 0:
            continue

        holdings[symbol] = quantity

    if not holdings:
        raise ValueError(
            "No holdings could be extracted from OCR text."
        )

    return holdings


def extract_holdings_from_image(image_path):
    """
    Extract holdings from a portfolio screenshot.

    Uses positional OCR for structured brokerage screenshots,
    then falls back to plain-text OCR for simple layouts.
    """

    image_path = str(image_path)

    image = Image.open(image_path)

    data = pytesseract.image_to_data(
        image,
        config="--psm 6",
        output_type=pytesseract.Output.DATAFRAME,
    )

    data = data.dropna(subset=["text"])

    data["text"] = (
        data["text"]
        .astype(str)
        .str.strip()
    )

    data = data[data["text"] != ""]

    if data.empty:
        raise ValueError(
            "No OCR text could be extracted from image."
        )

    # Keep reasonably confident OCR results.
    data = data[data["conf"] >= 40]

    if data.empty:
        raise ValueError(
            "OCR confidence was too low to extract holdings."
        )

    image_width = image.width

    # -----------------------------------------------------
    # Group OCR words into rows.
    # -----------------------------------------------------

    rows = []

    for _, word in data.sort_values(
        ["top", "left"]
    ).iterrows():

        placed = False

        for current_row in rows:

            reference_top = current_row[0]["top"]

            if abs(
                word["top"] - reference_top
            ) <= 12:

                current_row.append(word)
                placed = True
                break

        if not placed:
            rows.append([word])

    holdings = {}

    # -----------------------------------------------------
    # Parse structured brokerage table.
    # -----------------------------------------------------

    for row_words in rows:

        row_words = sorted(
            row_words,
            key=lambda item: item["left"],
        )

        symbol = None

        # Find ticker in leftmost column.
        for word in row_words:

            text = word["text"].strip()

            x_position = word["left"]

            if x_position > image_width * 0.20:
                continue

            if not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9&.-]{1,14}",
                text,
            ):
                continue

            if text.upper() in {
                "SYMBOL",
                "COMPANY",
                "NAME",
                "HOLDINGS",
                "MY",
                "PORTFOLIO",
            }:
                continue

            symbol = normalize_symbol(text)
            break

        if symbol is None:
            continue

        # Find quantity.
        for word in row_words:

            text = word["text"].strip()

            x_position = word["left"]

            if not (
                image_width * 0.30
                <= x_position
                <= image_width * 0.45
            ):
                continue

            if not re.fullmatch(
                r"\d+(?:\.\d+)?",
                text,
            ):
                continue

            quantity = float(text)

            if quantity > 0:
                holdings[symbol] = quantity

            break

    # -----------------------------------------------------
    # Fallback for simple screenshots.
    # -----------------------------------------------------

    if not holdings:

        text = pytesseract.image_to_string(
            image,
            config="--psm 6",
        )

        return extract_holdings_from_text(text)

    return holdings




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