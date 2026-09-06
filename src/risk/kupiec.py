import math


def calculate_kupiec_test(
    backtest_results,
    confidence_level=0.95,
):
    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    if "VIOLATION" not in backtest_results.columns:
        raise ValueError(
            "Backtest results must contain "
            "a VIOLATION column."
        )

    total_observations = len(backtest_results)

    if total_observations == 0:
        raise ValueError(
            "Backtest results cannot be empty."
        )

    violations = int(
        backtest_results["VIOLATION"].sum()
    )

    expected_probability = (
        1 - confidence_level
    )

    observed_probability = (
        violations / total_observations
    )

    non_violations = (
        total_observations - violations
    )

    # Special case: zero violations
    # avoids log(0).
    if violations == 0:
        likelihood_null = (
            (1 - expected_probability)
            ** total_observations
        )

        likelihood_alternative = 1.0

    else:
        likelihood_null = (
            (1 - expected_probability)
            ** non_violations
        ) * (
            expected_probability
            ** violations
        )

        likelihood_alternative = (
            (1 - observed_probability)
            ** non_violations
        ) * (
            observed_probability
            ** violations
        )

    likelihood_ratio = (
        -2
        * math.log(
            likelihood_null
            / likelihood_alternative
        )
    )

    p_value = math.erfc(
        math.sqrt(likelihood_ratio / 2)
    )

    return {
        "total_observations": total_observations,
        "violations": violations,
        "expected_probability": expected_probability,
        "observed_probability": observed_probability,
        "likelihood_ratio": likelihood_ratio,
        "p_value": p_value,
    }