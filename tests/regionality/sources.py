"""Which sources the older regionality tests are about.

Those tests assert exact `sources` lists and decision lists. They stay exact for the sources that existed when they were written
(ORIGINAL) and ignore any source added since (LBDA, reg WO-07, and later ones), so adding a source never breaks them. A new
source's own behaviour is tested beside it (tests/lbda). The baseline comparison (baseline.py) treats added sources the same way.
"""
from scripts.edop.areas import source_registry

ORIGINAL = {'basinatlas_v1', 'cliopatria', 'hyde_3_5', 'lmr_v2_1', 'evolv2k_v4', 'geda', 'edops_derived',
            'opentopodata_mapzen', 'open_meteo_elevation'}


def _id(x):
    return x['id'] if isinstance(x, dict) else x.source_id


def original(items):
    """The entries of a sources list (dicts with an `id`) or of a decision list (Decisions) that belong to the original sources."""
    return [x for x in items if _id(x) in ORIGINAL]


def later_variables():
    """Band T payload variables of the sources added since (read from the registry)."""
    out = set()
    for sid, e in source_registry._registry().items():
        v = e['selects'].get('variables')
        if sid not in ORIGINAL and isinstance(v, list):
            out |= {x['payload'] for x in v if 'payload' in x}
    return out
