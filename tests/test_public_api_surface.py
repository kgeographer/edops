"""
test_public_api_surface.py
--------------------------
Locks the *public* API surface: the set of routes marked include_in_schema=True
(the ones Swagger and the generated API Guide document) must stay exactly the
four advertised endpoints, each with a summary. If a new route is added without
include_in_schema=False, or an internal route is accidentally exposed, this
fails and names the offender — so it can't reach a release unnoticed.

No DB needed: enumerates app.routes and hits the DB-free /health route.
"""

from fastapi.testclient import TestClient

from app.main import app

# (method, path) -- the entire documented public surface. Update deliberately,
# in the same commit that changes what the docs advertise.
EXPECTED_PUBLIC = {
    ("GET", "/api/health"),
    ("GET", "/api/signature"),
    ("GET", "/api/area"),
    ("GET", "/api/areas"),
}


def _public_operations():
    ops = set()
    for route in app.routes:
        if not getattr(route, "include_in_schema", False):
            continue
        for method in getattr(route, "methods", None) or []:
            if method in ("HEAD", "OPTIONS"):
                continue
            ops.add((method, route.path))
    return ops


def test_public_surface_is_exactly_the_advertised_four():
    actual = _public_operations()
    leaked = actual - EXPECTED_PUBLIC
    missing = EXPECTED_PUBLIC - actual
    assert not leaked, (
        f"Route(s) exposed in the public schema but not in the advertised set: {sorted(leaked)}. "
        f"Add include_in_schema=False, or update EXPECTED_PUBLIC + the docs."
    )
    assert not missing, (
        f"Advertised endpoint(s) missing from the public schema: {sorted(missing)}."
    )


def test_public_routes_each_have_a_summary():
    """Swagger's collapsed rows and the API Guide index rely on summary= being set."""
    missing = []
    for route in app.routes:
        if not getattr(route, "include_in_schema", False):
            continue
        if ("GET", route.path) in EXPECTED_PUBLIC and not getattr(route, "summary", None):
            missing.append(route.path)
    assert not missing, f"Public route(s) with no summary=: {sorted(missing)}"


def test_health_ok():
    """/health is DB-free; assert the exact advertised body."""
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
