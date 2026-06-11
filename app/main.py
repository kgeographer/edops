from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.web.pages import router as page_router

app = FastAPI(
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