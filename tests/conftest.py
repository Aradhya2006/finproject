import pytest


# Tests that take over 30 seconds, found with `pytest --durations`. The LSTM
# tests are slow too, so they are matched by name.
SLOW_TESTS = (
    "test_real_portfolio_a_oos_forecasting",
    "test_dynamic_vs_historical_var",
    "test_dynamic_var_validation",
    "test_dynamic_backtesting",
)


def pytest_collection_modifyitems(items):
    """Mark the slow tests, so `pytest -m "not slow"` runs the fast suite."""
    for item in items:
        if "lstm" in item.nodeid.lower() or any(name in item.nodeid for name in SLOW_TESTS):
            item.add_marker(pytest.mark.slow)
