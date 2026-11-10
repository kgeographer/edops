"""Missing values in the profile scripts, decided in one place and as the engine decides them (WO-08 A4).

BasinATLAS stores NoData as -9999. The engine turns it into a `no_data` status on the row; the public signature passes
the raw marker through, sometimes scaled (slope -999.9), so a negative number cannot be told from a real one (temperature).
The rule here: a signature value is missing when the engine's row for it is `no_data`; a value read straight from
public.basin06 is missing when it is the marker; a class code is missing when it is the marker."""

NODATA = -9999


def is_missing(raw):
    """A value read straight from basin06 that is absent or the source's NoData marker."""
    return raw is None or raw == NODATA


def clean(raw):
    """The value, or None where it is missing."""
    return None if is_missing(raw) else raw


def row_value(rows, key, value):
    """The signature's `value` for `key`, or None where the engine's row for it says no_data. rows: {variable: row}."""
    row = (rows or {}).get(key)
    return None if row is not None and row.get('status') == 'no_data' else value


def class_label(code, labels):
    """A class code's label, or None for the marker (it is not a class)."""
    return None if is_missing(code) else labels.get(code)
