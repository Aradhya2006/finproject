import pytest

from PIL import Image, ImageDraw, ImageFont

from src.input.ocr import (
    extract_holdings_from_image,
    create_current_ocr_portfolio,
)
from src.input.ocr import (
    normalize_symbol,
    extract_holdings_from_text,
)

from PIL import Image, ImageDraw, ImageFont

from src.input.ocr import (
    extract_holdings_from_image,
)

def test_normalize_symbol():

    assert normalize_symbol(
        " tcs "
    ) == "TCS"

    assert normalize_symbol(
        "infy"
    ) == "INFY"


def test_extract_holdings_from_text():

    text = """
    Portfolio Holdings

    TCS 10
    INFY 15
    RELIANCE 5
    """

    holdings = extract_holdings_from_text(
        text
    )

    print()
    print("OCR EXTRACTION TEST")
    print("=" * 60)
    print("Extracted holdings:")
    print(holdings)

    assert holdings == {
        "TCS": 10.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }


def test_extract_table_like_text():

    text = """
    TCS       10
    HCLTECH   20
    WIPRO     5
    """

    holdings = extract_holdings_from_text(
        text
    )

    assert holdings == {
        "TCS": 10.0,
        "HCLTECH": 20.0,
        "WIPRO": 5.0,
    }


def test_empty_text():

    with pytest.raises(ValueError):
        extract_holdings_from_text("")


def test_no_holdings():

    with pytest.raises(ValueError):
        extract_holdings_from_text(
            "Portfolio Holdings Current Value"
        )
        
        
def test_extract_holdings_from_image(tmp_path):

    image_path = (
        tmp_path / "portfolio.png"
    )

    image = Image.new(
        "RGB",
        (1200, 600),
        "white",
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "C:/Windows/Fonts/arial.ttf",
        48,
    )

    draw.text(
        (80, 60),
        "Portfolio Holdings",
        fill="black",
        font=font,
    )

    draw.text(
        (80, 180),
        "TCS       10",
        fill="black",
        font=font,
    )

    draw.text(
        (80, 270),
        "INFY      15",
        fill="black",
        font=font,
    )

    draw.text(
        (80, 360),
        "RELIANCE  5",
        fill="black",
        font=font,
    )

    image.save(image_path)

    holdings = extract_holdings_from_image(
        image_path
    )

    print()
    print("OCR IMAGE → HOLDINGS TEST")
    print("=" * 60)
    print(holdings)

    assert holdings == {
        "TCS": 10.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }
    
    
    
    
def test_create_current_ocr_portfolio(tmp_path):

    image_path = (
        tmp_path / "portfolio.png"
    )

    image = Image.new(
        "RGB",
        (1200, 600),
        "white",
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "C:/Windows/Fonts/arial.ttf",
        48,
    )

    draw.text(
        (80, 60),
        "Portfolio Holdings",
        fill="black",
        font=font,
    )

    draw.text(
        (80, 180),
        "TCS       10",
        fill="black",
        font=font,
    )

    draw.text(
        (80, 270),
        "INFY      15",
        fill="black",
        font=font,
    )

    draw.text(
        (80, 360),
        "RELIANCE  5",
        fill="black",
        font=font,
    )

    image.save(image_path)

    portfolio = create_current_ocr_portfolio(
        image_path
    )

    print()
    print("END-TO-END OCR PORTFOLIO TEST")
    print("=" * 60)

    print(
        "Detected:",
        portfolio["detected_holdings"],
    )

    print(
        "Verified:",
        portfolio["verified_holdings"],
    )

    print(
        "Prices:",
        portfolio["prices"],
    )

    print(
        "Portfolio value:",
        portfolio["portfolio_value"],
    )

    print(
        "Weights:",
        portfolio["weights"],
    )

    assert portfolio["detected_holdings"] == {
        "TCS": 10.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }

    assert portfolio["verified_holdings"] == {
        "TCS": 10.0,
        "INFY": 15.0,
        "RELIANCE": 5.0,
    }

    assert portfolio["portfolio_value"] > 0

    assert abs(
        sum(
            portfolio["weights"].values()
        ) - 1.0
    ) < 1e-10