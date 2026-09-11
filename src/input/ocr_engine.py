from pathlib import Path

import pytesseract
from PIL import Image


def extract_text_from_image(image_path):
    """
    Extract raw text from a portfolio screenshot.

    Parameters
    ----------
    image_path : str or Path
        Path to the screenshot.

    Returns
    -------
    str
        Raw OCR text.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Image path is not a file: {image_path}"
        )

    try:
        image = Image.open(image_path)
    except Exception as exc:
        raise ValueError(
            f"Unable to open image: {image_path}"
        ) from exc

    try:
        text = pytesseract.image_to_string(
            image,
            config="--psm 6",
        )
    except Exception as exc:
        raise RuntimeError(
            "OCR extraction failed."
        ) from exc

    return text