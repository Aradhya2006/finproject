import numpy as np
import pandas as pd

from src.risk.kupiec import calculate_kupiec_test


results = pd.DataFrame({
    "VIOLATION": [
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
})


statistics = calculate_kupiec_test(
    results,
    confidence_level=0.95,
)


print("Kupiec Test")
print("-" * 50)

for key, value in statistics.items():
    print(f"{key}: {value}")


assert statistics["total_observations"] == 10
assert statistics["violations"] == 1

assert np.isclose(
    statistics["expected_probability"],
    0.05,
)

assert np.isclose(
    statistics["observed_probability"],
    0.10,
)

assert statistics["likelihood_ratio"] >= 0

assert 0 <= statistics["p_value"] <= 1


print("\nKupiec test implementation passed!")