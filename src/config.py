"""Settings from a .env file in the project root."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file(path=ENV_FILE):
    """
    Set variables from a KEY=VALUE file. A variable already set in the
    environment wins, so a value set in the terminal overrides the file.
    Returns the names that were set.
    """
    if not path.is_file():
        return []

    loaded = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = (part.strip() for part in line.split("=", 1))
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]

        if key and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)

    return loaded
