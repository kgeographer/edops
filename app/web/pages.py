# from fastapi import APIRouter, Request
# from fastapi.templating import Jinja2Templates
#
# router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")
#
#
# @router.get("/")
# def index(request: Request):
#     return templates.TemplateResponse(
#         "index.html",
#         {"request": request}
#     )

from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
print("TEMPLATES_DIR =", TEMPLATES_DIR)

@router.get("/")
def index(request: Request):
    host = request.headers.get("host", "")
    if "edops" in host:
        return templates.TemplateResponse("edops.html", {"request": request})
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/edop")
def edop_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/edops", status_code=301)

@router.get("/sandbox")
def sandbox_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/sandbox/lookup", status_code=301)

@router.get("/sandbox/lookup")
def sandbox_lookup(request: Request):
    return templates.TemplateResponse("sandbox.html", {"request": request})

@router.get("/sandbox/explorer")
def sandbox_explorer(request: Request):
    return templates.TemplateResponse("explorer.html", {"request": request})

@router.get("/edops")
def edops(request: Request):
    return templates.TemplateResponse("edops.html", {"request": request})

@router.get("/polities")
def polities(request: Request):
    return templates.TemplateResponse("cliopatria.html", {"request": request})