"""Source registry for the engine path (regionality WO-04, Part C).

Reads documentation/EDOPS_source_registry.yaml once, at first use. check() answers, for one source and one request,
whether the source applies and which years of the span it covers. It judges availability only; what a route returns
is the route's own specification.

Reasons for a source that does not apply:
  outside_span, outside_footprint, below_coverage_floor   reported in the response's `sources` block (not_applied)
  not_permitted, not_served                               never reported: the source is left out of both lists
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[3] / 'documentation' / 'EDOPS_source_registry.yaml'

REPORTED_REASONS = ('outside_span', 'outside_footprint', 'below_coverage_floor')


@dataclass(frozen=True)
class Decision:
    source_id: str
    applied: bool
    reason: Optional[str] = None                 # None when applied
    span: Optional[Tuple[int, int]] = None       # the years to query (clipped), None when not applied or no span given


@lru_cache(maxsize=1)
def _registry():
    with open(REGISTRY_PATH, encoding='utf-8') as f:
        return {s['id']: s for s in yaml.safe_load(f)['sources']}


def entry(source_id):
    """The registry entry (`selects` and `describes`) for a source; KeyError if the id is unknown."""
    try:
        return _registry()[source_id]
    except KeyError:
        raise KeyError(f'unknown source {source_id!r}; known: {sorted(_registry())}') from None


def years_covered(source_id):
    """(first, last) year the source holds, or None for a source with no time axis."""
    yc = (entry(source_id)['selects'].get('time') or {}).get('years_covered')
    return tuple(yc) if yc else None


def check(source_id, span=None, geometry=None, permitted=None):
    """Does the source apply to this request?

    span       : (from_year, to_year) or None
    geometry   : the query geometry, for a regional source's footprint test (none is tested in stage 2)
    permitted  : optional set of source ids; a source outside it is skipped before any other test
    """
    selects = entry(source_id)['selects']
    if permitted is not None and source_id not in permitted:
        return Decision(source_id, False, 'not_permitted')
    if selects.get('status') != 'served':
        return Decision(source_id, False, 'not_served')

    fp = (selects.get('footprint') or {}).get('type')
    if fp == 'cells' and geometry is not None:
        raise NotImplementedError('the footprint test for regional sources arrives with GEDA (stage 3)')

    time = selects.get('time') or {}
    covered = time.get('years_covered')
    if span is None or not covered or time.get('outside_span') == 'nearest_step':
        return Decision(source_id, True, None, tuple(span) if span else None)
    lo, hi = max(covered[0], span[0]), min(covered[1], span[1])
    if lo > hi:
        return Decision(source_id, False, 'outside_span')
    return Decision(source_id, True, None, (lo, hi))


def _source_entry(source_id, note=None):
    d = entry(source_id)['describes']
    e = {'id': source_id, 'name': d.get('name'), 'version': d.get('version'),
         'citation': d.get('citation'), 'licence': d.get('licence')}   # licence None = not stated
    if note:
        e['note'] = note
    return e


def sources_block(decisions=(), used=(), notes=None):
    """The response's `sources` block: {'used': [...], 'not_applied': [...]}.

    decisions : check() results; applied ones are `used`, ones with a reported reason are `not_applied`;
                the rest (not_permitted, not_served) are left out of both lists
    used      : further source ids that contributed (BasinATLAS always, Cliopatria for a polity, the elevation service)
    notes     : optional {source_id: text} attached to that source's entry (e.g. HYDE's nearest step)
    """
    notes = notes or {}
    used_ids = list(used)
    not_applied = []
    for d in decisions:
        if d.applied:
            used_ids.append(d.source_id)
        elif d.reason in REPORTED_REASONS:
            not_applied.append({**_source_entry(d.source_id, notes.get(d.source_id)), 'reason': d.reason})
    return {'used': [_source_entry(i, notes.get(i)) for i in used_ids], 'not_applied': not_applied}
