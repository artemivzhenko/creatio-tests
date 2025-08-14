import json
from pathlib import Path
from typing import Optional

from ..page.page_object import PageObject
from ..page import CreatioAuthPage
from ..field_types import FieldType


_FIELD_TYPE_MAP = {
    "TEXT": FieldType.TEXT,
    "NUMBER": FieldType.NUMBER,
    "BOOLEAN": FieldType.BOOLEAN,
    "DATETIME": FieldType.DATETIME,
    "LOOKUP": FieldType.LOOKUP,
}


def _normalize_bool(x):
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
    return None


def load_page_config(client: CreatioAuthPage, config_path: Optional[str] = None) -> PageObject:
    p = Path(config_path or "page.json")
    if not p.exists():
        raise FileNotFoundError(f"config file not found: {str(p)}")
    data = json.loads(p.read_text(encoding="utf-8"))

    name = str(data.get("name", "Page")).strip() or "Page"
    wait_timeout_sec = int(data.get("wait_timeout_sec", 30))
    debug = bool(_normalize_bool(data.get("debug", False)))

    page = PageObject(name=name, client=client, default_wait_timeout_sec=wait_timeout_sec, debug=debug)

    fields = data.get("fields", [])
    if not isinstance(fields, list) or not fields:
        raise ValueError("fields array is empty")

    for idx, f in enumerate(fields):
        t_raw = str(f.get("type", "")).strip().upper()
        if t_raw not in _FIELD_TYPE_MAP:
            raise ValueError(f"unknown field type at index {idx}: {t_raw!r}")
        ftype = _FIELD_TYPE_MAP[t_raw]

        code = str(f.get("code", "")).strip()
        if not code:
            raise ValueError(f"missing code for field at index {idx}")

        title = f.get("title", None)
        if title is not None:
            title = str(title)

        readonly = f.get("readonly", None)
        if readonly is not None:
            rb = _normalize_bool(readonly)
            if rb is None:
                raise ValueError(f"invalid readonly for field {code}")
            readonly = rb

        strict_title = bool(_normalize_bool(f.get("strict_title", True)))

        required = f.get("required", None)
        if required is not None:
            rq = _normalize_bool(required)
            if rq is None:
                raise ValueError(f"invalid required for field {code}")
            required = rq

        lookup_values = f.get("lookup_values", None)
        if lookup_values is not None and not isinstance(lookup_values, list):
            raise ValueError(f"lookup_values must be list for field {code}")

        per_field_wait = f.get("wait_timeout_sec", None)
        if per_field_wait is not None:
            per_field_wait = int(per_field_wait)

        page.add_field(
            field_type=ftype,
            code=code,
            title=title,
            readonly=readonly,
            strict_title=strict_title,
            required=required,
            lookup_values=lookup_values,
            wait_timeout_sec=per_field_wait,
        )

    return page
