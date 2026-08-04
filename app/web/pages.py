from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
print("TEMPLATES_DIR =", TEMPLATES_DIR)

def _render(request: Request, name: str):
    return templates.TemplateResponse(request, name)


@router.get("/")
def index(request: Request):
    host = request.headers.get("host", "")
    if "edops" in host:
        return _render(request, "edops.html")
    if "workbench" in host:
        return _render(request, "workbench.html")
    return _render(request, "index.html")

@router.get("/about")
def about(request: Request):
    return _render(request, "about.html")

@router.get("/docs")
def docs_stub(request: Request):
    # Placeholder route (2026-08-04, DOCSv4 plumbing) -- reserves /docs for a future MkDocs
    # site, now that Swagger has moved to /api/schema. Will be superseded by static nginx
    # serving once MkDocs is built (§4 of the DOCSv4 TODO).
    return _render(request, "docs_stub.html")

@router.get("/edop")
def edop_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/edops", status_code=301)

@router.get("/sandbox")
def sandbox(request: Request):
    return _render(request, "sandbox_v3.html")

@router.get("/sandbox/lookup")
def sandbox_lookup_redirect():
    # Old sandbox.html is abandoned (Karl, 2026-08-03) -- no route renders it anymore. File stays
    # in the repo, harmless, just never called. Old bookmarks/links land on the new canonical /sandbox.
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
    return _render(request, "workbench.html")


@router.get("/cdop")
def cdop_pilot(request: Request):
    return _render(request, "cdop_pilot.html")

@router.get("/sandbox/lookup3")
def sandbox_v3(request: Request):
    return _render(request, "sandbox_v3.html")


# --- Computing Place reorg (2026-08-03): new canonical URLs under edops.computingplace.org.
# /sandbox and /sandbox/lookup above are already repointed (old sandbox.html abandoned); these two
# are purely additive -- /sandbox/explorer and /cdop stay exactly as they are, untouched.

@router.get("/explorer")
def explorer(request: Request):
    return _render(request, "explorer.html")

@router.get("/cdop_tests")
def cdop_tests(request: Request):
    return _render(request, "cdop_pilot.html")
