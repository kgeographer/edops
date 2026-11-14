"""check() for a regional source (regionality WO-05): the footprint test and coverage rule, against the local database.

GEDA is the one source with a `cells` footprint. Cases from the WO-02 notebook: the Kyiv basin (inside), basins at the
edge of the footprint (coverage 0.498 and 0.067), and places outside it (Chaco Canyon, Timbuktu).
"""
import pytest

from app.db.connection import db_connect
from scripts.edop.areas import source_registry as sr
from scripts.edop.areas.engine import _band_t_query

SPAN = (1300, 1400)
KYIV, EDGE, SPARSE = 2060448220, 1060044120, 1060264990   # L6 basins: fully inside, coverage 0.498, coverage 0.067


def basin(hybas_id):
    return '(SELECT geom FROM public.basin06 WHERE hybas_id = %s)', (hybas_id,)


def point_buffer(lon, lat, km):
    return 'ST_Buffer(ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)::geometry', (lon, lat, km * 1000.0)


@pytest.fixture(scope='module')
def conn():
    with db_connect() as c:
        yield c


def test_a_basin_inside_the_footprint_is_applied(conn):
    d = sr.check('geda', span=SPAN, geometry=basin(KYIV), conn=conn)
    assert (d.applied, d.reason, d.span, d.flag) == (True, None, SPAN, None)
    assert d.coverage == pytest.approx(1.0, abs=1e-3)


@pytest.mark.parametrize('geometry', [point_buffer(-107.96, 36.06, 10), point_buffer(-2.9833, 16.8167, 100)],
                         ids=['chaco_canyon', 'timbuktu_100km'])
def test_a_place_outside_the_footprint_is_outside_footprint(conn, geometry):
    d = sr.check('geda', span=SPAN, geometry=geometry, conn=conn)
    assert (d.applied, d.reason, d.span, d.coverage) == (False, 'outside_footprint', None, 0.0)


def test_coverage_just_under_half_is_applied_and_flagged_low(conn):
    d = sr.check('geda', span=SPAN, geometry=basin(EDGE), conn=conn)
    assert (d.applied, d.reason, d.flag) == (True, None, 'low_coverage')
    assert d.coverage == pytest.approx(0.498, abs=0.005)


def test_coverage_under_a_tenth_is_not_applied(conn):
    d = sr.check('geda', span=SPAN, geometry=basin(SPARSE), conn=conn)
    assert (d.applied, d.reason, d.span) == (False, 'below_coverage_floor', None)
    assert d.coverage == pytest.approx(0.067, abs=0.005)


def test_a_span_outside_the_years_needs_no_database_work():
    d = sr.check('geda', span=(500, 900))          # no geometry, no connection: returns before the footprint test
    assert (d.applied, d.reason) == (False, 'outside_span')


def test_a_span_straddling_the_start_is_clipped(conn):
    d = sr.check('geda', span=(980, 1010), geometry=basin(KYIV), conn=conn)
    assert (d.applied, d.span) == (True, (1000, 1010))


def test_permission_is_checked_before_the_footprint():
    d = sr.check('geda', span=SPAN, permitted={'lmr_v2_1'})      # no geometry needed: not reached
    assert (d.applied, d.reason) == (False, 'not_permitted')


def test_a_regional_source_without_geometry_or_connection_is_an_error(conn):
    with pytest.raises(ValueError, match='geometry and conn'):
        sr.check('geda', span=SPAN)
    with pytest.raises(ValueError, match='geometry and conn'):
        sr.check('geda', span=SPAN, geometry=basin(KYIV))


@pytest.mark.parametrize('coverage, expected', [
    (0.0999, (False, 'below_coverage_floor', None)),
    (0.1, (True, None, 'low_coverage')),
    (0.4999, (True, None, 'low_coverage')),
    (0.5, (True, None, None)),
    (1.0, (True, None, None)),
])
def test_coverage_rule_boundaries(coverage, expected):
    assert sr.coverage_outcome('geda', coverage) == expected


def test_a_source_without_a_coverage_rule_is_always_applied():
    assert sr.coverage_outcome('lmr_v2_1', 0.0) == (True, None, None)


def test_a_global_source_needs_no_geometry():
    assert sr.check('lmr_v2_1', span=SPAN).applied


@pytest.mark.parametrize('case', ['buffer', 'polygon'])
def test_the_engines_parameterized_geometry_matches_its_text_geometry(conn, case):
    """_band_t_query builds the geometry twice (SQL text for the existing blocks, parameters for the registry)."""
    if case == 'buffer':
        q = _band_t_query(50.4547, 30.5238, 100, 1300, 1400, conn, None, None)
    else:
        wkt = conn.execute('SELECT ST_AsText(geom) FROM public.basin06 WHERE hybas_id = %s', (KYIV,)).fetchone()[0]
        q = _band_t_query(None, None, 0, 1300, 1400, conn, wkt, None)
    geom_sql, params = q.geom
    area = conn.execute(f'SELECT ST_Area(({geom_sql})::geography)', params).fetchone()[0]
    assert area == pytest.approx(q.buf_area_m2, rel=1e-9)
