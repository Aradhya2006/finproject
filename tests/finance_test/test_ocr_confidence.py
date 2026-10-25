import pytest
import pytesseract
from PIL import Image, ImageDraw, ImageFont

from src.input.ocr import extract_holdings_detailed


def _tesseract_installed():
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


requires_tesseract = pytest.mark.skipif(
    not _tesseract_installed(), reason="Tesseract OCR is not installed"
)


def _font(size=28):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


@requires_tesseract
def test_detailed_extraction_returns_holdings_and_real_confidence(tmp_path):
    image = Image.new("RGB", (900, 300), "white")
    draw = ImageDraw.Draw(image)
    rows = [("Symbol", "Qty", "Avg"), ("TCS", "75", "3450.20"), ("INFY", "195", "1520.00")]
    for index, (symbol, qty, avg) in enumerate(rows):
        y = 20 + index * 60
        draw.text((20, y), symbol, fill="black", font=_font())
        draw.text((330, y), qty, fill="black", font=_font())
        draw.text((600, y), avg, fill="black", font=_font())
    path = tmp_path / "holdings.png"
    image.save(path)

    result = extract_holdings_detailed(path)

    assert result["holdings"] == {"TCS": 75.0, "INFY": 195.0}
    assert 0 < result["confidence"] <= 1
    assert "TCS" in result["raw_text"]


@requires_tesseract
def test_blank_image_is_rejected(tmp_path):
    path = tmp_path / "blank.png"
    Image.new("RGB", (300, 200), "white").save(path)

    with pytest.raises(ValueError):
        extract_holdings_detailed(path)
