"""
test_codebook_alignment.py
--------------------------
Validates that the live signature payload matches the codebook.

Two tests:
  1. Every implemented field with an api_key is accessible somewhere in the
     response (profile_groups items or profile_summary).
  2. Every implemented field that appears in profile_groups is in the band
     declared by the codebook.

Any future drift between codebook and code will surface here first.
"""

import csv
from pathlib import Path

import pytest

CODEBOOK = Path(__file__).parent.parent / "documentation" / "EDOPS_variable_catalog_v0.3.tsv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _codebook_implemented(exclude_bands=None):
    """Return all rows with status=implemented, optionally excluding bands."""
    exclude = set(exclude_bands or [])
    with CODEBOOK.open() as f:
        return [
            row for row in csv.DictReader(f, delimiter="\t")
            if row["status"] == "implemented" and row["band"] not in exclude
        ]


def _all_accessible_keys(sig):
    """
    Collect every key reachable in the response:
      - top-level scalar keys
      - keys in profile_groups items
      - keys in profile_summary items
    """
    keys = set(sig.keys())
    for bdata in sig.get("profile_groups", {}).values():
        for item in bdata.get("items", []):
            keys.add(item["key"])
    for item in sig.get("profile_summary", []):
        keys.add(item["key"])
    return keys


def _profile_groups_values(sig):
    """Return a flat {key: value} dict built from all profile_groups items."""
    values = {}
    for bdata in sig.get("profile_groups", {}).values():
        for item in bdata.get("items", []):
            values[item["key"]] = item["value"]
    return values


def _profile_groups_index(sig):
    """
    Return {api_key: band_letter} for every field in profile_groups.
    Used to check band placement.
    """
    index = {}
    for band, bdata in sig.get("profile_groups", {}).items():
        for item in bdata.get("items", []):
            index[item["key"]] = band
    return index


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_codebook_file_exists():
    assert CODEBOOK.exists(), f"Codebook not found: {CODEBOOK}"


def test_implemented_fields_accessible(timbuktu_sig):
    """
    Every implemented field with an api_key_s or api_key_u is reachable
    in the payload. Failures mean either the codebook is wrong (field marked
    implemented but not delivered) or the code is wrong (field dropped from
    query or profile_groups).
    """
    accessible = _all_accessible_keys(timbuktu_sig)
    missing = []

    for row in _codebook_implemented(exclude_bands=["T", "output"]):
        for col in ("api_key_s", "api_key_u"):
            key = (row.get(col) or "").strip()
            if key and key not in accessible:
                missing.append(
                    f"  {row['schema_key']:35s} {col}='{key}'"
                )

    assert not missing, (
        f"{len(missing)} implemented field(s) missing from payload:\n"
        + "\n".join(missing)
    )


def test_implemented_fields_in_declared_band(timbuktu_sig):
    """
    For fields that appear in profile_groups, each must be in the band
    declared by the codebook. Failures indicate a band mismatch between
    codebook and PROFILE_GROUPS in signature.py.

    Fields not in any profile_group (top-level only, profile_summary only)
    are skipped — they have no band placement to validate.
    """
    pg_index = _profile_groups_index(timbuktu_sig)
    wrong = []

    for row in _codebook_implemented(exclude_bands=["T", "output"]):
        key = (row.get("api_key_s") or "").strip()
        declared_band = row["band"].strip()

        if not key or key not in pg_index:
            continue  # not in profile_groups — nothing to check here

        actual_band = pg_index[key]
        if actual_band != declared_band:
            wrong.append(
                f"  {row['schema_key']:35s} '{key}': "
                f"codebook=Band {declared_band}, payload=Band {actual_band}"
            )

    assert not wrong, (
        f"{len(wrong)} field(s) in wrong band:\n"
        + "\n".join(wrong)
    )


def test_no_unexpected_none_values(timbuktu_sig):
    """
    Spot-check that core implemented fields return non-None values for
    Timbuktu. A None here means the DB view is missing data for this basin,
    or the field was added to the codebook before the view was updated.
    """
    # These should always be populated for any valid L8 basin
    must_have_value = [
        "elev_min", "elev_max", "slope_avg", "lith_class",
        "discharge_yr", "runoff", "temp_yr", "precip_yr", "aridity",
        "biome", "ecoregion",
        "pop_density", "gdp_avg",
        "dist_sink",
    ]
    flat = _profile_groups_values(timbuktu_sig)
    nulls = [k for k in must_have_value if flat.get(k) is None]
    assert not nulls, f"Unexpected None values for Timbuktu: {nulls}"
