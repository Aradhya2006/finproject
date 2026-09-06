import math


def calculate_christoffersen_test(
    backtest_results,
):
    if "VIOLATION" not in backtest_results.columns:
        raise ValueError(
            "Backtest results must contain "
            "a VIOLATION column."
        )

    violations = (
        backtest_results["VIOLATION"]
        .astype(int)
        .to_numpy()
    )

    if len(violations) < 2:
        raise ValueError(
            "At least two observations are required."
        )

    n00 = 0
    n01 = 0
    n10 = 0
    n11 = 0

    for i in range(1, len(violations)):
        previous = violations[i - 1]
        current = violations[i]

        if previous == 0 and current == 0:
            n00 += 1
        elif previous == 0 and current == 1:
            n01 += 1
        elif previous == 1 and current == 0:
            n10 += 1
        elif previous == 1 and current == 1:
            n11 += 1

    n0 = n00 + n01
    n1 = n10 + n11

    # Probability of a violation after
    # a non-violation.
    pi01 = (
        n01 / n0
        if n0 > 0
        else 0.0
    )

    # Probability of a violation after
    # a violation.
    pi11 = (
        n11 / n1
        if n1 > 0
        else 0.0
    )

    # Probability of a violation under
    # the unrestricted model.
    total_transitions = n00 + n01 + n10 + n11

    pi = (
        (n01 + n11) / total_transitions
    )

    # Log-likelihood under the independence
    # model.
    log_likelihood_independent = 0.0

    if n00 > 0:
        log_likelihood_independent += (
            n00 * math.log(1 - pi)
        )

    if n01 > 0:
        log_likelihood_independent += (
            n01 * math.log(pi)
        )

    if n10 > 0:
        log_likelihood_independent += (
            n10 * math.log(1 - pi)
        )

    if n11 > 0:
        log_likelihood_independent += (
            n11 * math.log(pi)
        )

    # Log-likelihood under the Markov
    # transition model.
    log_likelihood_markov = 0.0

    if n00 > 0 and pi01 < 1:
        log_likelihood_markov += (
            n00 * math.log(1 - pi01)
        )

    if n01 > 0 and pi01 > 0:
        log_likelihood_markov += (
            n01 * math.log(pi01)
        )

    if n10 > 0 and pi11 < 1:
        log_likelihood_markov += (
            n10 * math.log(1 - pi11)
        )

    if n11 > 0 and pi11 > 0:
        log_likelihood_markov += (
            n11 * math.log(pi11)
        )

    likelihood_ratio = (
        -2
        * (
            log_likelihood_independent
            - log_likelihood_markov
        )
    )

    # Chi-square distribution with 1 degree
    # of freedom.
    p_value = math.erfc(
        math.sqrt(
            max(likelihood_ratio, 0) / 2
        )
    )

    return {
        "n00": n00,
        "n01": n01,
        "n10": n10,
        "n11": n11,
        "pi01": pi01,
        "pi11": pi11,
        "likelihood_ratio": likelihood_ratio,
        "p_value": p_value,
    }



def calculate_conditional_coverage_test(
    kupiec_results,
    christoffersen_results,
):
    kupiec_lr = kupiec_results["likelihood_ratio"]

    independence_lr = (
        christoffersen_results["likelihood_ratio"]
    )

    likelihood_ratio = (
        kupiec_lr + independence_lr
    )

    # Chi-square distribution with 2 degrees
    # of freedom.
    #
    # Survival function:
    # P(X >= LR) = exp(-LR / 2)
    #
    # This closed form applies to chi-square(2).

    p_value = math.exp(
        -likelihood_ratio / 2
    )

    return {
        "likelihood_ratio": likelihood_ratio,
        "p_value": p_value,
    }