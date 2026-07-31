from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
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
    title="Environmental Dimensions of Place Service (EDOPS)",
    description="A component of [Computing Place](https://computingplace.org).\n\n[API Guide](https://edops.computingplace.org/static/api_guide.html) · [Variable catalog](https://edops.computingplace.org/documentation/EDOPS_variable_catalog_v0.3.tsv) · [Schema](https://edops.computingplace.org/documentation/edops_schema.json)",
    version="0.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(api_router)
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

# Dev harness: serve exemplar fixtures at /dev/exemplars/ for the fixture-based renderer.
# output/ is gitignored and absent on the server; the mount silently skips if the dir
# does not exist so startup is unaffected in non-dev environments.
try:
    app.mount("/dev/exemplars", StaticFiles(directory="output/edop/surface/exemplars"), name="dev_exemplars")
except RuntimeError:
    pass