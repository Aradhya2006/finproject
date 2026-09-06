import numpy as np
import pandas as pd

from src.risk.christoffersen import (
    calculate_christoffersen_test,
)


results = pd.DataFrame({
    "VIOLATION": [
        False,
        False,
        True,
        False,
        False,
        True,
        False,
        False,
        False,
        True,
    ]
})


statistics = calculate_christoffersen_test(
    results
)


print("Christoffersen Independence Test")
print("-" * 60)

for key, value in statistics.items():
    print(f"{key}: {value}")


assert statistics["n00"] == 4
assert statistics["n01"] == 3
assert statistics["n10"] == 2
assert statistics["n11"] == 0

assert np.isclose(
    statistics["pi01"],
    3 / 7,
)

assert np.isclose(
    statistics["pi11"],
    0.0,
)

assert statistics["likelihood_ratio"] >= 0

assert 0 <= statistics["p_value"] <= 1


print(
    "\nChristoffersen test implementation passed!"
)