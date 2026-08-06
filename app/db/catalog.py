"""
catalog.py — Variable catalog accessor.

Loads EDOPS_variable_catalog_v0.4.tsv once at import time, keyed by schema_key.
Provides direction-agnostic lookups used by the similarity registry and any other
code that needs to translate between schema keys, DB column names, and labels.

Key columns used:
  schema_key      — canonical variable identifier (e.g. "precipitation_annual")
  basin08_col_s   — sub-basin DB column  (e.g. "pre_mm_syr"); empty for Derived vars
  basin08_col_u   — upstream DB column   (e.g. "pre_mm_uyr"); empty for Derived vars
  friendly_name   — human-readable label (e.g. "Precipitation annual")
  units           — unit string
  source          — "BasinATLAS v1.0", "Derived", etc.
"""

import csv
from pathlib import Path
from typing import Dict, Optional

_CATALOG_PATH = Path(__file__).parent.parent.parent / "documentation" / "EDOPS_variable_catalog_v0.4.tsv"

# Loaded once; keyed by schema_key.
_BY_KEY: Dict[str, Dict[str, str]] = {}

# Reverse maps: DB column name → schema_key
_BY_COL: Dict[str, str] = {}


def _load() -> None:
    global _BY_KEY, _BY_COL
    if _BY_KEY:
        return
    if not _CATALOG_PATH.exists():
        return
    with _CATALOG_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            key = (row.get("schema_key") or "").strip()
            if not key:
                continue
            entry = {
                "schema_key":    key,
                "friendly_name": (row.get("friendly_name") or "").strip(),
                "units":         (row.get("units") or "").strip(),
                "source":        (row.get("source") or "").strip(),
                "col_s":         (row.get("basin08_col_s") or "").strip(),
                "col_u":         (row.get("basin08_col_u") or "").strip(),
                "band":          (row.get("band") or "").strip(),
                "dimension":     (row.get("dimension") or "").strip(),
            }
            _BY_KEY[key] = entry
            if entry["col_s"]:
                _BY_COL[entry["col_s"]] = key
            if entry["col_u"]:
                _BY_COL[entry["col_u"]] = key


_load()


def col_for(schema_key: str, su: str = "s") -> Optional[str]:
    """Return the DB column name for a schema_key.

    su='s' → sub-basin column (basin08_col_s)
    su='u' → upstream column  (basin08_col_u)

    Returns None for Derived variables (no DB column) or unknown keys.
    """
    entry = _BY_KEY.get(schema_key)
    if entry is None:
        return None
    col = entry["col_s"] if su == "s" else entry["col_u"]
    return col or None


def label_for(schema_key: str) -> str:
    """Return the friendly_name for a schema_key, or the key itself if not found."""
    entry = _BY_KEY.get(schema_key)
    return entry["friendly_name"] if entry else schema_key


def units_for(schema_key: str) -> str:
    """Return the units string for a schema_key, or '' if not found."""
    entry = _BY_KEY.get(schema_key)
    return entry["units"] if entry else ""


def schema_for_col(col_name: str) -> Optional[str]:
    """Return the schema_key for a DB column name, or None if not found."""
    _load()
    return _BY_COL.get(col_name)


def is_derived(schema_key: str) -> bool:
    """True if the variable has no DB column (computed from monthly arrays or other logic)."""
    entry = _BY_KEY.get(schema_key)
    if entry is None:
        return False
    return not entry["col_s"] and not entry["col_u"]


def get(schema_key: str) -> Optional[Dict[str, str]]:
    """Return the full catalog entry for a schema_key, or None if not found."""
    return _BY_KEY.get(schema_key)
