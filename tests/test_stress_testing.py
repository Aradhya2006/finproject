from src.risk.stress_testing import (
    calculate_stress_loss,
    calculate_stress_loss_value,
)


def test_stress_testing():

    weights = {
        "TCS": 0.25,
        "INFY": 0.25,
        "HCLTECH": 0.20,
        "WIPRO": 0.15,
        "RELIANCE": 0.15,
    }

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

    print("\nStress Test")
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


if __name__ == "__main__":
    test_stress_testing()
    print("\nStress testing test passed!")