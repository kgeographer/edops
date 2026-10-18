"""Signature query log: one row per successful /api/signature or /api/areas request.

src='ui' = user-initiated GUI request (carries place_name); 'workbench' = Workbench lookup;
'api' = no src tag (external callers, coordinates only). src='ui_aux' requests are the GUI's
parallel/silent duplicates and are not logged. Fail-soft: a logging problem never affects a response.
"""
import asyncio
import logging

from fastapi import FastAPI, Request

from app.db.connection import db_connect

log = logging.getLogger(__name__)

LOGGED_PATHS = {"/api/signature", "/api/areas"}

_DDL = """
CREATE TABLE IF NOT EXISTS public.query_log (
    id          bigserial PRIMARY KEY,
    ts          timestamptz NOT NULL DEFAULT now(),
    endpoint    text NOT NULL,
    src         text NOT NULL,
    scope       text,
    place_name  text,
    polity      text,
    year        integer,
    lat         double precision,
    lon         double precision,
    radius_km   double precision,
    level       integer,
    bands       text,
    user_agent  text
)
"""
_INSERT = """
INSERT INTO public.query_log
    (endpoint, src, scope, place_name, polity, year, lat, lon, radius_km, level, bands, user_agent)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def ensure_table() -> None:
    try:
        conn = db_connect()
        try:
            conn.execute(_DDL)
            conn.commit()
        finally:
            conn.close()
    except Exception:
        log.exception("query_log: could not ensure table; logging disabled until fixed")


def _num(q, key, cast):
    try:
        return cast(q[key]) if key in q else None
    except ValueError:
        return None


def _write(row: tuple) -> None:
    try:
        conn = db_connect()
        try:
            conn.execute(_INSERT, row)
            conn.commit()
        finally:
            conn.close()
    except Exception:
        log.exception("query_log: insert failed")


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def _log_queries(request: Request, call_next):
        response = await call_next(request)
        if request.url.path in LOGGED_PATHS and response.status_code == 200:
            q = request.query_params
            src = q.get("src", "api")
            if src != "ui_aux":
                row = (
                    request.url.path, src[:20], q.get("scope"),
                    (q.get("place_name") or "")[:200] or None, q.get("polity"),
                    _num(q, "year", int), _num(q, "lat", float), _num(q, "lon", float),
                    _num(q, "radius_km", float), _num(q, "level", int), q.get("bands"),
                    (request.headers.get("user-agent") or "")[:200] or None,
                )
                asyncio.get_running_loop().run_in_executor(None, _write, row)
        return response
