"""Regression baseline (regionality WO-03, Part A): signature payloads against the reference files.

Added fields are allowed; a changed or removed field fails. Reference files are re-captured only at a stage boundary,
with Karl's approval: python scripts/edop/regionality/capture_baseline.py --force
"""
import pytest
from fastapi.testclient import TestClient

from tests.regionality import baseline as bl


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# compare(): the semantics the baseline relies on (no DB)
# ---------------------------------------------------------------------------
def _row(variable, value, year=None):
    return {"band": "T", "variable": variable, "year": year, "epoch_year": None, "representative_raw": value}


def test_identical_payloads_have_no_differences():
    p = {"scope": "x", "rows": [_row("a", 1.0, 1300), _row("a", 2.0, 1301)]}
    assert bl.compare(p, p) == []


def test_added_fields_and_rows_are_allowed():
    ref = {"scope": "x", "rows": [_row("a", 1.0, 1300)]}
    new = {"scope": "x", "extra": 1, "rows": [_row("geda", 0.5, 1300), _row("a", 1.0, 1300)]}
    assert bl.compare(ref, new) == []


def test_removed_field_fails():
    d = bl.compare({"scope": "x", "caveats": {"k": "v"}}, {"scope": "x"})
    assert [(p, k) for p, k, *_ in d] == [(".caveats", "removed")]


def test_removed_row_fails():
    ref = {"rows": [_row("a", 1.0, 1300), _row("a", 2.0, 1301)]}
    new = {"rows": [_row("a", 1.0, 1300)]}
    assert [k for _, k, *_ in bl.compare(ref, new)] == ["removed"]


def test_changed_value_fails_but_float_noise_does_not():
    ref = {"rows": [_row("a", 1000.0, 1300)]}
    assert bl.compare(ref, {"rows": [_row("a", 1000.0 * (1 + 1e-10), 1300)]}) == []
    assert [k for _, k, *_ in bl.compare(ref, {"rows": [_row("a", 1000.1, 1300)]})] == ["changed"]


def test_changed_string_and_list_length_fail():
    assert bl.compare({"s": "a"}, {"s": "b"})[0][1] == "changed"
    assert bl.compare({"bands": ["A", "B"]}, {"bands": ["A"]})[0][1] == "changed"


# ---------------------------------------------------------------------------
# The baseline itself
# ---------------------------------------------------------------------------
def test_every_request_has_a_reference_file():
    missing = [n for n in bl.REQUESTS if not bl.ref_path(n).exists()]
    assert not missing, f"no reference file for {missing}: run scripts/edop/regionality/capture_baseline.py"


@pytest.mark.parametrize("name", list(bl.REQUESTS))
def test_payload_matches_reference(name, client, db_available):
    if not db_available:
        pytest.skip("DB not available")
    diffs = bl.compare(bl.load_ref(name), bl.fetch(client, name))
    shown = "\n".join(f"  {p}: {kind} (reference {a!r}, now {b!r})" for p, kind, a, b in diffs[:20])
    assert not diffs, f"{name}: {len(diffs)} difference(s) from the reference\n{shown}"
