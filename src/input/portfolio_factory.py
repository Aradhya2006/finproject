from src.input.manual import create_current_manual_portfolio
from src.input.ocr import create_current_ocr_portfolio
from src.input.value_input import create_value_portfolio


def create_portfolio(
    input_type,
    data,
    confirmed_holdings=None,
):
    """
    Create a standardized PortfolioInput from any
    supported portfolio input method.

    Parameters
    ----------
    input_type : str
        "manual", "ocr", or "value"

    data :
        Input data required by the selected method.

    confirmed_holdings : dict, optional
        User-confirmed or edited OCR holdings.

    Returns
    -------
    PortfolioInput
    """

    if not isinstance(input_type, str):
        raise ValueError(
            "Input type must be a string."
        )

    input_type = input_type.strip().lower()

    if input_type == "manual":
        return create_current_manual_portfolio(data)

    if input_type == "ocr":
        return create_current_ocr_portfolio(
            data,
            confirmed_holdings=confirmed_holdings,
        )

    if input_type == "value":
        return create_value_portfolio(data)

    raise ValueError(
        f"Unsupported input type: {input_type}"
    )