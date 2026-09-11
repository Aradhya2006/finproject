def verify_holdings(
    detected_holdings,
    confirmed_holdings=None,
):
    """
    Verify OCR-detected holdings.

    If confirmed_holdings is provided, use the
    user-confirmed values. Otherwise, return the
    detected holdings for user review.

    Parameters
    ----------
    detected_holdings : dict
        Holdings extracted by OCR.

    confirmed_holdings : dict, optional
        Holdings confirmed or edited by the user.

    Returns
    -------
    dict
        Verified holdings.
    """

    if not isinstance(
        detected_holdings,
        dict,
    ):
        raise ValueError(
            "Detected holdings must be a dictionary."
        )

    if not detected_holdings:
        raise ValueError(
            "Detected holdings cannot be empty."
        )

    if confirmed_holdings is None:
        return detected_holdings.copy()

    if not isinstance(
        confirmed_holdings,
        dict,
    ):
        raise ValueError(
            "Confirmed holdings must be a dictionary."
        )

    if not confirmed_holdings:
        raise ValueError(
            "Confirmed holdings cannot be empty."
        )

    return confirmed_holdings.copy()