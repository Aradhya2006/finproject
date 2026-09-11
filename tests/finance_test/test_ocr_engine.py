from PIL import Image, ImageDraw, ImageFont

from src.input.ocr_engine import (
    extract_text_from_image,
)


def test_extract_text_from_image(tmp_path):

    image_path = (
        tmp_path / "portfolio.png"
    )

    image = Image.new(
        "RGB",
        (1200, 600),
        "white",
    )

    draw = ImageDraw.Draw(image)

    font_path = (
        "C:/Windows/Fonts/arial.ttf"
    )

    font = ImageFont.truetype(
        font_path,
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

    text = extract_text_from_image(
        image_path
    )

    print()
    print("OCR ENGINE TEST")
    print("=" * 60)
    print(text)

    assert isinstance(text, str)

    assert "TCS" in text
    assert "INFY" in text
    assert "RELIANCE" in text