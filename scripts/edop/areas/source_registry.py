"""Source registry for the engine path (regionality WO-04, Part C).

Reads documentation/EDOPS_source_registry.yaml once, at first use. check() answers, for one source and one request,
whether the source applies: its years against the span, and for a regional source (footprint type `cells`) its cells
against the query geometry, with the coverage rule. It judges availability only; what a route returns is the route's
own specification.

Reasons for a source that does not apply:
  outside_span, outside_footprint, below_coverage_floor   reported in the response's `sources` block (not_applied)
  not_permitted, not_served                               never reported: the source is left out of both lists
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

import yaml
from psycopg import sql

REGISTRY_PATH = Path(__file__).resolve().parents[3] / 'documentation' / 'EDOPS_source_registry.yaml'

REPORTED_REASONS = ('outside_span', 'outside_footprint', 'below_coverage_floor')


@dataclass(frozen=True)
class Decision:
    source_id: str
    applied: bool
    reason: Optional[str] = None                 # None when applied
    span: Optional[Tuple[int, int]] = None       # the years to query (clipped), None when not applied or no span given
    coverage: Optional[float] = None             # regional sources: share of the query area inside the source's cells
    flag: Optional[str] = None                   # 'low_coverage' when applied below the source's ok_from


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


def coverage_outcome(source_id, coverage):
    """The source's coverage rule applied to a coverage share: (applied, reason, flag).

    Below low_coverage_from: not applied (below_coverage_floor). From there to ok_from: applied, flagged low_coverage.
    From ok_from: applied. A source with no coverage_rule is always applied."""
    rule = entry(source_id)['selects'].get('coverage_rule')
    if not rule:
        return True, None, None
    if coverage < rule['low_coverage_from']:
        return False, 'below_coverage_floor', None
    if coverage < rule['ok_from']:
        return True, None, 'low_coverage'
    return True, None, None


def _footprint_stats(conn, footprint, geometry):
    """(number of cells overlapping the geometry, share of the geometry's area inside them).

    footprint : the entry's `footprint` block; `test` is 'schema.table.column' of the cell geometries (from the YAML)
    geometry  : (SQL expression for the query geometry, parameters), e.g. ('ST_GeomFromText(%s, 4326)', (wkt,))"""
    schema, table, column = footprint['test'].split('.')
    geom_sql, params = geometry
    query = sql.SQL("""
        WITH g AS (SELECT {geom} AS geom),
        hit AS (
            SELECT ST_Area(ST_Intersection(c.{col}, g.geom)::geography) AS ov
            FROM {tbl} c, g WHERE ST_Intersects(c.{col}, g.geom))
        SELECT count(*) FILTER (WHERE ov > 0),
               coalesce(sum(ov) FILTER (WHERE ov > 0), 0),
               (SELECT ST_Area(geom::geography) FROM g)
        FROM hit""").format(geom=sql.SQL(geom_sql), col=sql.Identifier(column), tbl=sql.Identifier(schema, table))
    n_cells, overlap_m2, query_m2 = conn.execute(query, params).fetchone()
    return int(n_cells), (float(overlap_m2) / float(query_m2) if query_m2 else 0.0)


def check(source_id, span=None, geometry=None, permitted=None, conn=None):
    """Does the source apply to this request?

    span       : (from_year, to_year) or None
    geometry   : (SQL expression, parameters) for the query geometry; needed with conn for a regional source
    permitted  : optional set of source ids; a source outside it is skipped before any other test
    conn       : database connection, used only for a regional source's footprint test

    Order: permission, status, years (no database work when the span is outside), then footprint and coverage.
    """
    selects = entry(source_id)['selects']
    if permitted is not None and source_id not in permitted:
        return Decision(source_id, False, 'not_permitted')
    if selects.get('status') != 'served':
        return Decision(source_id, False, 'not_served')

    time = selects.get('time') or {}
    covered = time.get('years_covered')
    if span is None or not covered or time.get('outside_span') == 'nearest_step':
        years = tuple(span) if span else None
    else:
        lo, hi = max(covered[0], span[0]), min(covered[1], span[1])
        if lo > hi:
            return Decision(source_id, False, 'outside_span')
        years = (lo, hi)

    footprint = selects.get('footprint') or {}
    if footprint.get('type') != 'cells':
        return Decision(source_id, True, None, years)
    if geometry is None or conn is None:
        raise ValueError(f'{source_id}: a regional source needs geometry and conn for its footprint test')
    n_cells, coverage = _footprint_stats(conn, footprint, geometry)
    if n_cells == 0:
        return Decision(source_id, False, 'outside_footprint', None, 0.0)
    applied, reason, flag = coverage_outcome(source_id, coverage)
    if not applied:
        return Decision(source_id, False, reason, None, coverage)
    return Decision(source_id, True, None, years, coverage, flag)


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
