from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_sandbox import router as api_sandbox_router
from app.api.routes_common import router as api_common_router
from app.api.routes_cliopatria import router as api_cliopatria_router
from app.api.routes_explorer import router as api_explorer_router
from app.api.routes_workbench import router as api_workbench_router
from app.web.pages import router as page_router
from app.db.connection import db_connect
from app.db.seasonality import load_similarity_index
from app.db.context import load_context_index
from app.db.climate_classes import load_class_index
from app.db.societies_scan import load_societies_scan_substrate


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = db_connect()
    try:
        load_similarity_index(conn, level=6)
        load_similarity_index(conn, level=8)
        load_context_index(conn, level=6)
        load_context_index(conn, level=8)
        load_class_index(conn, level=6)   # L06 eager (~1.5 s); L08 lazy on first use (WO7a)
    finally:
        conn.close()
    load_societies_scan_substrate()   # CITYKIN WO4 -- small (1,133-row) parquet, no DB conn needed
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/schema",
    title="Environmental Dimensions of Place Service (EDOPS)",
    description="A component of [Computing Place](https://computingplace.org).\n\n[API Guide](https://edops.computingplace.org/static/api_guide.html) · [Variable catalog](https://edops.computingplace.org/documentation/EDOPS_variable_catalog_v0.4.tsv) · [Schema](https://edops.computingplace.org/documentation/edops_schema.json)",
    version="0.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(api_sandbox_router)
app.include_router(api_common_router)
app.include_router(api_cliopatria_router)
app.include_router(api_explorer_router)
app.include_router(api_workbench_router)
app.include_router(page_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

app.mount(
    "/documentation",
    StaticFiles(directory="documentation"),
    name="documentation"
)

# MkDocs site (2026-08-05, DOCSv4): docsite/ is the tracked source; `mkdocs build` compiles it
# to site/ (gitignored). check_dir=False so the app still starts if site/ hasn't been built yet
# -- /docs just 404s until someone runs `mkdocs build`. At deploy time this mount can be
# superseded by an nginx-level static serve of site/ (independent of FastAPI restarts), but
# isn't required to -- this works in both local dev and production as-is.
app.mount(
    "/docs",
    StaticFiles(directory="site", html=True, check_dir=False),
    name="docs"
)

# Dev harness: serve exemplar fixtures at /dev/exemplars/ for the fixture-based renderer.
# output/ is gitignored and absent on the server; the mount silently skips if the dir
# does not exist so startup is unaffected in non-dev environments.
try:
    app.mount("/dev/exemplars", StaticFiles(directory="output/edop/surface/exemplars"), name="dev_exemplars")
except RuntimeError:
    pass