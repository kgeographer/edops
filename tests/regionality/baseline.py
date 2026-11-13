"""Regression baseline for signature payloads (regionality WO-03, Part A).

REQUESTS is the fixed set. capture() writes each response as a gzipped JSON reference file under baseline_reference/;
compare() checks a new response against its reference: added fields are allowed, a changed or removed field is a
difference. Numbers match within a small tolerance (Band T sums vary in the last digits between identical calls).
Reference files are re-captured only at a stage boundary, with Karl's approval (scripts/edop/regionality/capture_baseline.py).
"""
import gzip
import json
import math
from pathlib import Path
from unittest.mock import patch

REF_DIR = Path(__file__).parent / 'baseline_reference'

# name -> (route under /api/, query params). Calls go through the real routes with FastAPI's test client.
TIMBUKTU = dict(lat=16.8167, lon=-2.9833)
TBILISI = dict(lat=41.7151, lon=44.8271)
BRUGES = dict(lat=51.2093, lon=3.2247)       # the flat-city fixture of the terrain lens (CITYKIN WO1a)
KYIV = dict(lat=50.4547, lon=30.5238)        # L6 basin 2060448220
_AE = dict(level=6, bands='ABCDE', detail='true')
_T = dict(level=6, bands='T', detail='true')
REQUESTS = {
    'timbuktu_single_basin_L6': ('areas', dict(scope='single_basin', **TIMBUKTU, **_AE)),
    'timbuktu_buffer100_L6': ('areas', dict(scope='buffer', radius_km=100, **TIMBUKTU, **_AE)),
    'tbilisi_single_basin_L6': ('areas', dict(scope='single_basin', **TBILISI, **_AE)),
    'bruges_single_basin_L6': ('areas', dict(scope='single_basin', **BRUGES, **_AE)),
    'northern_song_961_L6': ('areas', dict(scope='polity', polity='Northern Song', year=961, **_AE)),
    'timbuktu_bandT_1236_1240': ('areas', dict(scope='single_basin', **TIMBUKTU, from_year=1236, to_year=1240, **_T)),
    'timbuktu_bandT_1300_1400': ('areas', dict(scope='single_basin', **TIMBUKTU, from_year=1300, to_year=1400, **_T)),
    'kyiv_bandT_1236_1240': ('areas', dict(scope='single_basin', **KYIV, from_year=1236, to_year=1240, **_T)),
    'kyiv_bandT_1300_1400': ('areas', dict(scope='single_basin', **KYIV, from_year=1300, to_year=1400, **_T)),
    'timbuktu_public_signature': ('signature', dict(scope='basin', level=6, bands='ABCE', **TIMBUKTU)),
    # added 2026-11-13 (WO-04), captured from the code before the Band T refactor: the buffer geometry branch with the
    # HYDE 1950 epoch, a polity with Band T, and a span past LMR and eVolv2k
    'timbuktu_buffer100_bandT_1940_1960': ('areas', dict(scope='buffer', radius_km=100, **TIMBUKTU, from_year=1940, to_year=1960, **_T)),
    'northern_song_bandT_950_970': ('areas', dict(scope='polity', polity='Northern Song', year=961, from_year=950, to_year=970, **_T)),
    'timbuktu_bandT_2010_2020': ('areas', dict(scope='single_basin', **TIMBUKTU, from_year=2010, to_year=2020, **_T)),
}

# Paths (dot-joined, list indexes dropped) that legitimately vary between identical calls.
IGNORE = ('.meta.generated',)

# The public signature looks up the point elevation from OpenTopoData (a live external call); pinned so the baseline is offline.
PINNED_ELEVATION = {'elev_point': 267.0, 'elev_source': 'opentopodata', 'elev_dataset': 'mapzen', 'elev_resolution_m': 30}

REL_TOL, ABS_TOL = 1e-6, 1e-9
ROW_KEY = ('band', 'variable', 'year', 'epoch_year')


def fetch(client, name):
    route, params = REQUESTS[name]
    with patch('app.db.signature.get_elevation_point', return_value=dict(PINNED_ELEVATION)):
        r = client.get(f'/api/{route}', params=params)
    assert r.status_code == 200, f'{name}: HTTP {r.status_code}: {r.text[:200]}'
    return r.json()


def ref_path(name):
    return REF_DIR / f'{name}.json.gz'


def save_ref(name, payload):
    REF_DIR.mkdir(exist_ok=True)
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    with gzip.GzipFile(ref_path(name), 'wb', mtime=0) as f:     # mtime=0: identical bytes for identical content
        f.write(raw)


def load_ref(name):
    with gzip.open(ref_path(name), 'rb') as f:
        return json.loads(f.read())


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _row_keys(lst):
    """Keys that identify rows in a list of signature rows, or None if the list is not such a list."""
    if not lst or not all(isinstance(r, dict) and 'variable' in r for r in lst):
        return None
    seen, keys = {}, []
    for r in lst:
        k = tuple(r.get(f) for f in ROW_KEY)
        seen[k] = seen.get(k, 0) + 1
        keys.append(k + (seen[k],))
    return keys


def compare(ref, new, path=''):
    """Differences between a reference payload and a new one: [(path, kind, reference, new)].
    Fields only in `new` are allowed and not reported; kind is 'removed', 'changed' or 'type'."""
    here = path.replace('[]', '')
    if any(here == p or here.startswith(p + '.') for p in IGNORE):
        return []
    if isinstance(ref, dict):
        if not isinstance(new, dict):
            return [(path, 'type', type(ref).__name__, type(new).__name__)]
        out = []
        for k, v in ref.items():
            if k not in new:
                out.append((f'{path}.{k}', 'removed', v if not isinstance(v, (dict, list)) else '...', None))
            else:
                out += compare(v, new[k], f'{path}.{k}')
        return out
    if isinstance(ref, list):
        if not isinstance(new, list):
            return [(path, 'type', 'list', type(new).__name__)]
        rk, nk = _row_keys(ref), _row_keys(new)
        if rk is not None and nk is not None:               # signature rows: match by identity, extra rows allowed
            by_key = dict(zip(nk, new))
            out = []
            for k, r in zip(rk, ref):
                label = f'{path}[{"/".join(str(x) for x in k)}]'
                out += compare(r, by_key[k], label) if k in by_key else [(label, 'removed', 'row', None)]
            return out
        if len(ref) != len(new):
            return [(path, 'changed', f'list of {len(ref)}', f'list of {len(new)}')]
        return [d for i, (a, b) in enumerate(zip(ref, new)) for d in compare(a, b, f'{path}[{i}]')]
    if _is_num(ref) and _is_num(new):
        if math.isclose(ref, new, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            return []
        return [(path, 'changed', ref, new)]
    return [] if ref == new else [(path, 'changed', ref, new)]
