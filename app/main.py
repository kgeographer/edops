from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

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
    docs_url=None,  # custom /api/schema route below, adds swagger_custom.css on top of the default
    title="EDOPS API",
    description=(
        "EDOPS — the Environmental Dimensions of Place Service — provides programmatic "
        "access to structured environmental signatures for any location on Earth. A "
        "signature characterizes a drainage basin, or a set of basins for areal queries "
        "like a buffer scope or historical polity, using BasinATLAS hydrology, "
        "climate, and terrain variables, with optional historical enrichment from LMR "
        "v2.1 paleoclimate, HYDE 3.4 land-use history, and eVolv2k v4 volcanic forcing. \n\n"
        "[API Guide](/docs/api/) · "
        "[Sample settlement signature response](/documentation/edops_schema.json)"
    ),
    version="0.4"
)
# "[API Guide](https://edops.computingplace.org/docs/api/) · "

SWAGGER_LOGO_HEADER = (
    '<div class="edops-swagger-header">'
    '<a href="/edops"><img src="/static/images/edops_header_400.jpg" alt="EDOPS"></a>'
    '<p>Environmental Dimensions of Place Service (EDOPS)</p>'
    '</div>'
)


@app.get("/api/schema", include_in_schema=False)
async def custom_swagger_ui():
    # Minimal EDOPS presence, not the full site header -- this page is reached only via
    # one nested link from the API Guide modal, not a site-wide nav entry, so the visitor
    # already has full site context; the logo alone avoids a jarring identity shift
    # without dragging in Bootstrap/site.css for nav pills and modal links that don't
    # even resolve on a standalone page.
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " — Schema",
        # Hides the Schemas panel -- with no response_model= declared anywhere, it only
        # ever shows the two generic 422 validation-error shapes, nothing else.
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
    content = html.body.decode("utf-8").replace(
        "</head>",
        '<link rel="stylesheet" href="/static/css/swagger_custom.css"></head>',
    ).replace("<body>", "<body>" + SWAGGER_LOGO_HEADER).replace(
        "</body>",
        # deepLinking is on by default; setting the hash (rather than reloading with it)
        # lets Swagger UI's own deep-link listener open + scroll to /signature on first load.
        "<script>if (!window.location.hash) "
        "{ window.location.hash = '#/api/signature_api_signature_get'; }</script></body>",
    )
    return HTMLResponse(content)

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