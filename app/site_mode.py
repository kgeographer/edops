"""The v1 alpha site mode (EDOPS_SITE_MODE=v1alpha): the new pages only, kept out of search engines.

In this mode the 0.4 pages answer 404 with a short page pointing at the live 0.4 site, every response carries
X-Robots-Tag: noindex, and /robots.txt disallows everything. The setting is read per request, so tests can switch it.
Without the setting nothing here does anything.
"""
from fastapi import Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from app.settings import settings

V04_PAGES = ("/sandbox", "/workbench", "/polities", "/about")     # 0.4 page routes; /sandbox/* too (old aliases)


def is_alpha() -> bool:
    return settings.EDOPS_SITE_MODE == "v1alpha"


def is_v04_page(path: str) -> bool:
    return path in V04_PAGES or path.startswith("/sandbox/")


def _pointer_page() -> str:
    live = settings.EDOPS_LIVE_V04_URL
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>Not in the v1 alpha</title>'
            f'<style>body{{font-family:system-ui,sans-serif;max-width:36rem;margin:4rem auto;padding:0 16px;color:#222}}</style></head><body>'
            f'<h1 style="font-size:1.3rem">Not in the v1 alpha</h1>'
            f'<p>This page belongs to EDOPS v0.4 and is not part of the v1 alpha.</p>'
            f'<p><a href="{live}">The live v0.4 site</a> &middot; <a href="/edops">Back to the v1 alpha</a></p></body></html>')


def install(app):
    @app.get("/robots.txt", include_in_schema=False)
    def robots():
        if not is_alpha():
            return PlainTextResponse("Not found", status_code=404)
        return PlainTextResponse("User-agent: *\nDisallow: /\n")

    @app.middleware("http")
    async def v1alpha(request: Request, call_next):
        if not is_alpha():
            return await call_next(request)
        if is_v04_page(request.url.path):
            response = HTMLResponse(_pointer_page(), status_code=404)
        else:
            response = await call_next(request)
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response
