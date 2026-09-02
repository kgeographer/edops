from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
print("TEMPLATES_DIR =", TEMPLATES_DIR)


def _static_mtime(relpath: str) -> int:
    """Cache-bust stamp for a static asset that changes during active work."""
    try:
        return int((STATIC_DIR / relpath).stat().st_mtime)
    except OSError:
        return 0


def _render(request: Request, name: str, **context):
    return templates.TemplateResponse(request, name, context)


@router.get("/")
def index(request: Request):
    host = request.headers.get("host", "")
    if "edops" in host:
        return _render(request, "edops.html")
    if "workbench" in host:
        return _render(request, "workbench.html",
                       lovejoy_v=_static_mtime("workbench/lovejoy_regions.geojson"))
    return _render(request, "index.html")

@router.get("/about")
def about(request: Request):
    return _render(request, "about.html")

@router.get("/edop")
def edop_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/edops", status_code=301)

@router.get("/sandbox")
def sandbox(request: Request):
    return _render(request, "sandbox.html")

@router.get("/sandbox/lookup")
def sandbox_lookup_redirect():
    # Old Lookup page is abandoned (Karl, 2026-08-03) -- no route renders it anymore. Renamed to
    # sandbox_v03.html and kept in app/templates/, harmless, just never called. Old bookmarks/links
    # land on the new canonical /sandbox.
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/sandbox", status_code=301)

@router.get("/sandbox/explorer")
def sandbox_explorer(request: Request):
    return _render(request, "explorer.html")

@router.get("/edops")
def edops(request: Request):
    return _render(request, "edops.html")

@router.get("/polities")
def polities(request: Request):
    return _render(request, "cliopatria.html")

@router.get("/workbench")
def workbench(request: Request):
    return _render(request, "workbench.html",
                   lovejoy_v=_static_mtime("workbench/lovejoy_regions.geojson"))

@router.get("/sandbox/lookup3")
def sandbox_lookup3_compat(request: Request):
    return _render(request, "sandbox.html")


# --- Computing Place reorg (2026-08-03): new canonical URLs under edops.computingplace.org.
# /sandbox and /sandbox/lookup above are already repointed (old sandbox.html abandoned);
# /sandbox/explorer stays exactly as it is, untouched.

@router.get("/explorer")
def explorer(request: Request):
    return _render(request, "explorer.html")
