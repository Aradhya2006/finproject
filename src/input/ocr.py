import re

import pandas as pd
import pytesseract
from PIL import Image

# Importing ocr_engine configures the Tesseract executable path.
from src.input import ocr_engine  # noqa: F401
from src.data.current_prices import get_latest_prices
from src.input.manual import calculate_portfolio_from_holdings
from src.input.verification import verify_holdings


MIN_WORD_CONFIDENCE = 40      # Tesseract confidence (0-100) below which words are ignored
ROW_TOLERANCE_PX = 12         # vertical distance that still counts as the same table row
SYMBOL_COLUMN_MAX_X = 0.20    # ticker is expected in the left 20% of the image
QUANTITY_MIN_X = 0.30         # quantity is expected between 30% and 45% of the width
QUANTITY_MAX_X = 0.45

# Table headers that look like tickers but are not.
NON_SYMBOL_WORDS = {"SYMBOL", "COMPANY", "NAME", "HOLDINGS", "MY", "PORTFOLIO"}


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


def _read_words(image):
    """Run Tesseract and return one row per recognized, non-empty word."""

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

    data = data[data["text"] != ""].copy()

    if data.empty:
        raise ValueError(
            "No OCR text could be extracted from image."
        )

    data["conf"] = pd.to_numeric(data["conf"], errors="coerce").fillna(-1)

    return data


def _group_rows(words):
    """Group words into table rows by their vertical position."""

    rows = []

    for _, word in words.sort_values(["top", "left"]).iterrows():

        for current_row in rows:
            if abs(word["top"] - current_row[0]["top"]) <= ROW_TOLERANCE_PX:
                current_row.append(word)
                break
        else:
            rows.append([word])

    return rows


def _find_symbol_word(row_words, image_width):
    """Return the leftmost ticker-like word in the symbol column, if any."""

    for word in row_words:

        text = word["text"]

        if word["left"] > image_width * SYMBOL_COLUMN_MAX_X:
            continue

        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9&.-]{1,14}", text):
            continue

        if text.upper() in NON_SYMBOL_WORDS:
            continue

        return word

    return None


def _find_quantity_word(row_words, image_width, symbol_left):
    """
    Return the quantity word for a row.

    Looks in the usual quantity column first. If the layout differs, falls
    back to the first whole number to the right of the ticker.
    """

    def is_number(word):
        return re.fullmatch(r"\d+(?:\.\d+)?", word["text"]) is not None

    for word in row_words:
        in_column = image_width * QUANTITY_MIN_X <= word["left"] <= image_width * QUANTITY_MAX_X
        if in_column and is_number(word):
            return word

    for word in row_words:
        if word["left"] > symbol_left and re.fullmatch(r"\d+", word["text"]):
            return word

    return None


def extract_holdings_detailed(image_path):
    """
    Extract holdings from a portfolio screenshot, with confidence.

    Returns a dict:
        holdings   - {symbol: quantity}
        confidence - mean Tesseract confidence of the words used, 0-1
        raw_text   - recognized text, one table row per line

    Uses positional OCR for structured brokerage screenshots, then falls
    back to plain-text OCR for simple layouts.
    """

    image = Image.open(str(image_path))

    words = _read_words(image)
    confident = words[words["conf"] >= MIN_WORD_CONFIDENCE]

    if confident.empty:
        raise ValueError(
            "OCR confidence was too low to extract holdings."
        )

    image_width = image.width

    holdings = {}
    used_confidences = []
    row_texts = []

    for row_words in _group_rows(confident):

        row_words = sorted(row_words, key=lambda item: item["left"])
        row_texts.append(" ".join(word["text"] for word in row_words))

        symbol_word = _find_symbol_word(row_words, image_width)

        if symbol_word is None:
            continue

        quantity_word = _find_quantity_word(row_words, image_width, symbol_word["left"])

        if quantity_word is None:
            continue

        quantity = float(quantity_word["text"])

        if quantity <= 0:
            continue

        holdings[normalize_symbol(symbol_word["text"])] = quantity
        used_confidences.extend([symbol_word["conf"], quantity_word["conf"]])

    if holdings:
        confidence = sum(used_confidences) / len(used_confidences) / 100
        return {
            "holdings": holdings,
            "confidence": round(confidence, 4),
            "raw_text": "\n".join(row_texts),
        }

    # Simple screenshot layout: parse free text instead.
    text = pytesseract.image_to_string(image, config="--psm 6")
    holdings = extract_holdings_from_text(text)
    confidence = confident["conf"].mean() / 100

    return {
        "holdings": holdings,
        "confidence": round(float(confidence), 4),
        "raw_text": text.strip(),
    }


def extract_holdings_from_image(image_path):
    """
    Extract holdings from a portfolio screenshot. Returns {symbol: quantity}.
    """

    return extract_holdings_detailed(image_path)["holdings"]


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

    raw_prices = get_latest_prices(
        list(verified_holdings.keys())
    )

    # Strip _sources metadata before passing to portfolio calculation
    raw_prices.pop("_sources", None)

    portfolio = calculate_portfolio_from_holdings(
        verified_holdings,
        raw_prices,
    )

    portfolio.detected_holdings = detected_holdings
    portfolio.verified_holdings = verified_holdings

    return portfolio
