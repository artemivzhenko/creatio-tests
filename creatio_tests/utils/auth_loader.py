import json
from pathlib import Path
from typing import Optional

from ..page import CreatioAuthPage


def _as_bool(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("1", "true", "yes", "y", "on"):
            return True
        if s in ("0", "false", "no", "n", "off"):
            return False
    if isinstance(x, (int, float)):
        return bool(x)
    raise ValueError(f"cannot cast to bool: {x!r}")


def load_auth(config_path: Optional[str] = None) -> CreatioAuthPage:
    p = Path(config_path or "auth.json")
    if not p.exists():
        raise FileNotFoundError(f"config file not found: {str(p)}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"invalid json in {str(p)}: {e}")

    required = ["base_url", "username", "password", "test_url"]
    missing = [k for k in required if k not in data or data.get(k) is None or str(data.get(k)).strip() == ""]
    if missing:
        raise ValueError(f"missing required keys: {missing}")

    base_url = str(data["base_url"]).strip()
    username = str(data["username"])
    password = str(data["password"])
    test_url = str(data["test_url"])

    headless = data.get("headless", False)
    try:
        headless = _as_bool(headless)
    except ValueError as e:
        raise ValueError(f"invalid 'headless': {e}")

    debug = data.get("debug", True)
    try:
        debug = _as_bool(debug)
    except ValueError as e:
        raise ValueError(f"invalid 'debug': {e}")

    wait_timeout_sec = data.get("wait_timeout_sec", 180)
    try:
        wait_timeout_sec = int(wait_timeout_sec)
    except Exception:
        raise ValueError(f"invalid 'wait_timeout_sec': {wait_timeout_sec!r}")

    return CreatioAuthPage(
        base_url=base_url,
        username=username,
        password=password,
        test_url=test_url,
        headless=headless,
        wait_timeout_sec=wait_timeout_sec,
        debug=debug,
    )
