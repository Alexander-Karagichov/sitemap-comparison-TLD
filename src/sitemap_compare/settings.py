import json
import os


def load_settings(path: str) -> dict:
    """Return saved settings, or {} if the file is missing or unreadable."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(path: str, data: dict) -> None:
    """Write settings to ``path`` as pretty JSON (UTF-8)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
