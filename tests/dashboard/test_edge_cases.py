"""WO-10: a point within 5 km of a basin is moved to it and the response says so; further away, a plain 404; bad input, a plain 422."""
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.dashboard

INSIDE = dict(lat=31.2001, lon=29.9187)   # Alexandria
# WHG places that fall in no basin (gaz.whg_gaz, hybas_id_l06 null)
SNAPS = [("Bulukumba", -5.583, 120.217), ("Arsuz", 36.433, 35.850), ("Pevensey Castle", 50.772, 0.361)]
SEA = dict(lat=0.0, lon=-30.0)


def _get(path, **params):
    from app.main import app
    return TestClient(app).get(path, params=dict(params, src="ui_aux"))


def test_point_inside_a_basin_is_not_moved():
    r = _get("/api/areas", scope="single_basin", level=6, **INSIDE)
    assert r.status_code == 200 and "point_moved" not in r.json()


@pytest.mark.parametrize("level", [6, 8])
@pytest.mark.parametrize("name,lat,lon", SNAPS)
def test_whg_place_outside_every_basin_is_moved_and_says_so(name, lat, lon, level):
    r = _get("/api/areas", scope="single_basin", level=level, lat=lat, lon=lon)
    assert r.status_code == 200, name
    m = r.json()["point_moved"]
    assert 0 < m["distance_m"] <= m["max_m"] == 5000 and m["from"] == dict(lat=lat, lon=lon)


@pytest.mark.parametrize("path,extra", [("/api/signature", dict(scope="basin")), ("/api/areas", dict(scope="basin_ring"))])
def test_the_public_basin_and_ring_routes_move_it_too(path, extra):
    r = _get(path, level=6, lat=SNAPS[1][1], lon=SNAPS[1][2], **extra)
    assert r.status_code == 200 and r.json()["point_moved"]["distance_m"] > 0


def test_no_basin_within_5_km_is_a_plain_404():
    r = _get("/api/signature", scope="basin", level=8, **SEA)
    b = r.json()
    assert r.status_code == 404 and "5 km" in b["detail"] and b["reason"] == "no_basin_nearby" and b["nearest_basin_km"] > 5


@pytest.mark.parametrize("params,named", [(dict(lat=91, lon=10), "lat"), (dict(lat=10, lon=181), "lon"), (dict(lat="abc", lon=10), "lat")])
def test_bad_coordinates_name_the_parameter(params, named):
    r = _get("/api/signature", scope="basin", **params)
    assert r.status_code == 422 and r.json()["detail"].startswith(named + ":")


def test_profile_snap_is_the_engines_snap():
    from app.db.connection import db_connect
    from scripts.edop.areas.engine import SNAP_M, snap_to_basin
    from scripts.edop.whg import wo08_units
    assert wo08_units.SNAP_M == SNAP_M == 5000.0
    conn = db_connect()
    try:
        _, lat, lon = SNAPS[0]
        assert wo08_units.snap_point(conn, lat, lon) == snap_to_basin(conn, lat, lon, 6)
    finally:
        conn.close()
