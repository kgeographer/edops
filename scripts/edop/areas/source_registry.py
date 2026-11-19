"""Source registry for the engine path (regionality WO-04, Part C).

Reads documentation/EDOPS_source_registry.yaml once, at first use. check() answers, for one source and one request,
whether the source applies: its years against the span, and for a regional source (footprint type `cells`) its cells
against the query geometry, with the coverage rule. It judges availability only; what a route returns is the route's
own specification.

Reasons for a source that does not apply:
  outside_span, outside_footprint, below_coverage_floor   reported in the response's `sources` block (not_applied)
  not_permitted, not_served                               never reported: the source is left out of both lists

A source whose cells have data only from a cell-specific year on (`coverage_rule.per_year`, footprint `first_year_column`;
LBDA) is judged year by year: coverage in a year is the share of the query area inside the cells that have a value that
year. It never falls as the years go on, so the years that meet the floor are one run to the end of the span; the span is
clipped to it (the earlier years get no rows) and the Decision carries each year's coverage.
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
    requested_span: Optional[Tuple[int, int]] = None   # the span as asked, when given; `span` is what is returned
    coverage_by_year: Optional[dict] = None      # per-year sources only: {year: coverage} for the returned years


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


def year_caveats(source_id, year):
    """Caveat keys for a year the source flags: its `year_flags` entries that name a `caveat` and cover the year."""
    flags = entry(source_id)['selects'].get('year_flags') or []
    return [f['caveat'] for f in flags if f.get('caveat') and f['years'][0] <= year <= f['years'][1]]


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


def _footprint_cells(conn, footprint, geometry):
    """([(first_year, overlap in m2) for each cell overlapping the geometry], area of the geometry in m2), for a source
    whose cells have data from a cell-specific year (the footprint's `first_year_column`)."""
    schema, table, column = footprint['test'].split('.')
    geom_sql, params = geometry
    query = sql.SQL("""
        WITH g AS (SELECT {geom} AS geom)
        SELECT c.{fy}, ST_Area(ST_Intersection(c.{col}, g.geom)::geography),
               (SELECT ST_Area(geom::geography) FROM g)
        FROM {tbl} c, g WHERE ST_Intersects(c.{col}, g.geom)""").format(
        geom=sql.SQL(geom_sql), fy=sql.Identifier(footprint['first_year_column']), col=sql.Identifier(column),
        tbl=sql.Identifier(schema, table))
    rows = [(int(f), float(ov), float(q)) for f, ov, q in conn.execute(query, params).fetchall() if ov and ov > 0]
    return [(f, ov) for f, ov, _ in rows], (rows[0][2] if rows else 0.0)


def _per_year_decision(source_id, footprint, lo, hi, requested, geometry, conn):
    """check() for a per-year source: cells by first year, coverage for each year lo..hi, the span clipped to the years that
    meet the coverage floor."""
    cells, query_m2 = _footprint_cells(conn, footprint, geometry)
    if not cells:
        return Decision(source_id, False, 'outside_footprint', None, 0.0, requested_span=requested)
    by_first = {}
    for f, ov in cells:
        by_first[f] = by_first.get(f, 0.0) + ov
    firsts = sorted(by_first)
    cov = {}
    for y in range(lo, hi + 1):
        cov[y] = sum(by_first[f] for f in firsts if f <= y) / query_m2 if query_m2 else 0.0
    floor = entry(source_id)['selects']['coverage_rule']['low_coverage_from']
    passing = [y for y in range(lo, hi + 1) if cov[y] >= floor]
    if not passing:
        return Decision(source_id, False, 'below_coverage_floor', None, cov[hi], requested_span=requested)
    span = (passing[0], hi)
    applied, reason, flag = coverage_outcome(source_id, cov[hi])
    return Decision(source_id, True, None, span, cov[hi], flag, requested, {y: cov[y] for y in range(span[0], span[1] + 1)})


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
    requested = tuple(span) if span else None
    if span is None or not covered or time.get('outside_span') == 'nearest_step':
        years = tuple(span) if span else None
    else:
        lo, hi = max(covered[0], span[0]), min(covered[1], span[1])
        if lo > hi:
            return Decision(source_id, False, 'outside_span', requested_span=requested)
        years = (lo, hi)

    footprint = selects.get('footprint') or {}
    if footprint.get('type') != 'cells':
        return Decision(source_id, True, None, years, requested_span=requested)
    if geometry is None or conn is None:
        raise ValueError(f'{source_id}: a regional source needs geometry and conn for its footprint test')
    if (selects.get('coverage_rule') or {}).get('per_year') and footprint.get('first_year_column'):
        if years is None:
            years = (covered[1], covered[1])             # no span asked: judge the latest year
        return _per_year_decision(source_id, footprint, years[0], years[1], requested, geometry, conn)
    n_cells, coverage = _footprint_stats(conn, footprint, geometry)
    if n_cells == 0:
        return Decision(source_id, False, 'outside_footprint', None, 0.0, requested_span=requested)
    applied, reason, flag = coverage_outcome(source_id, coverage)
    if not applied:
        return Decision(source_id, False, reason, None, coverage, requested_span=requested)
    return Decision(source_id, True, None, years, coverage, flag, requested)


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
    clipped = {}
    not_applied = []
    for d in decisions:
        if d.applied:
            used_ids.append(d.source_id)
            if d.requested_span and d.span and tuple(d.requested_span) != tuple(d.span):
                clipped[d.source_id] = {'requested': list(d.requested_span), 'returned': list(d.span)}
        elif d.reason in REPORTED_REASONS:
            not_applied.append({**_source_entry(d.source_id, notes.get(d.source_id)), 'reason': d.reason})
    entries = []
    for i in used_ids:
        e = _source_entry(i, notes.get(i))
        if i in clipped:
            e['years'] = clipped[i]                  # the span was clipped to what the source covers (or covers well enough)
        entries.append(e)
    return {'used': entries, 'not_applied': not_applied}
