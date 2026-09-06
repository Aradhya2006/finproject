from src.risk.stress_testing import (
    calculate_stress_loss,
    calculate_stress_loss_value,
    evaluate_stress_scenarios,
)


def test_stress_testing():

    weights = {
        "TCS": 0.25,
        "INFY": 0.25,
        "HCLTECH": 0.20,
        "WIPRO": 0.15,
        "RELIANCE": 0.15,
    }

    # --------------------------------------------------
    # Test 1: Single stress scenario
    # --------------------------------------------------

    shocks = {
        "TCS": -0.20,
        "INFY": -0.20,
        "HCLTECH": -0.20,
        "WIPRO": -0.20,
        "RELIANCE": -0.10,
    }

    stress_return = calculate_stress_loss(
        weights,
        shocks,
    )

    portfolio_value = 1_000_000

    stress_loss = calculate_stress_loss_value(
        stress_return,
        portfolio_value,
    )

    assert stress_return < 0
    assert stress_loss > 0

    print("\nSingle Stress Test")
    print("-" * 40)

    print(
        f"Portfolio stress return: "
        f"{stress_return * 100:.2f}%"
    )

    print(
        f"Portfolio value: "
        f"₹{portfolio_value:,.2f}"
    )

    print(
        f"Stress loss: "
        f"₹{stress_loss:,.2f}"
    )

    # --------------------------------------------------
    # Test 2: Multiple stress scenarios
    # --------------------------------------------------

    scenarios = {

        "IT Sector Crash": {
            "TCS": -0.20,
            "INFY": -0.20,
            "HCLTECH": -0.20,
            "WIPRO": -0.20,
            "RELIANCE": -0.10,
        },

        "Broad Market Crash": {
            "TCS": -0.15,
            "INFY": -0.15,
            "HCLTECH": -0.15,
            "WIPRO": -0.15,
            "RELIANCE": -0.15,
        },

        "Reliance Shock": {
            "TCS": -0.05,
            "INFY": -0.05,
            "HCLTECH": -0.05,
            "WIPRO": -0.05,
            "RELIANCE": -0.30,
        },

        "Moderate Downturn": {
            "TCS": -0.10,
            "INFY": -0.10,
            "HCLTECH": -0.10,
            "WIPRO": -0.10,
            "RELIANCE": -0.10,
        },
    }

    results = evaluate_stress_scenarios(
        weights,
        scenarios,
    )

    assert len(results) == len(scenarios)

    assert all(
        value < 0
        for value in results.values()
    )

    print("\nMultiple Stress Scenarios")
    print("-" * 40)

    for scenario_name, stress_return in results.items():

        stress_loss = calculate_stress_loss_value(
            stress_return,
            portfolio_value,
        )

        print(
            f"{scenario_name}: "
            f"{stress_return * 100:.2f}% "
            f"loss = "
            f"₹{stress_loss:,.2f}"
        )


if __name__ == "__main__":
    test_stress_testing()
    print("\nStress testing test passed!")