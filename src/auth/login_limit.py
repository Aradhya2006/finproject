"""
Limits password guesses. After too many wrong passwords from one address,
that address is locked out for a while, even for the right password.

The counts are kept in memory, so they reset when the server restarts.
"""

import time


MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60
LOCKOUT_SECONDS = 15 * 60

_failures = {}  # address -> times of recent wrong passwords
_locked_until = {}  # address -> time the lockout ends


def retry_after(address):
    """Seconds until this address may try again, or 0 if it may try now."""
    remaining = _locked_until.get(address, 0) - time.time()
    return int(remaining) + 1 if remaining > 0 else 0


def record_failure(address):
    now = time.time()
    recent = [t for t in _failures.get(address, []) if now - t < WINDOW_SECONDS]
    recent.append(now)

    if len(recent) >= MAX_FAILURES:
        _locked_until[address] = now + LOCKOUT_SECONDS
        _failures.pop(address, None)
    else:
        _failures[address] = recent


def record_success(address):
    _failures.pop(address, None)
    _locked_until.pop(address, None)


def reset():
    """Forget every count and lockout. Used by the tests."""
    _failures.clear()
    _locked_until.clear()
