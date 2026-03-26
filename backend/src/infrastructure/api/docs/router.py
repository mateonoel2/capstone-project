"""Client API documentation pages served via Jinja2 templates."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from src.infrastructure.api.docs.content import (
    API_BASE_PLACEHOLDER,
    ENDPOINTS,
    get_endpoints_by_group,
)

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)

router = APIRouter(prefix="/api/docs", include_in_schema=False)

_ENDPOINT_MAP = {ep.slug: ep for ep in ENDPOINTS}


def _get_base_url(request: Request) -> str:
    """Derive the public API base URL from the incoming request."""
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
    return f"{scheme}://{host}"


def _common_context(active_slug: str) -> dict:
    return {
        "groups": get_endpoints_by_group(),
        "active_slug": active_slug,
    }


def _render(template_name: str, request: Request, **kwargs) -> HTMLResponse:
    tpl = _env.get_template(template_name)
    html = tpl.render(**kwargs)
    html = html.replace(API_BASE_PLACEHOLDER, _get_base_url(request))
    return HTMLResponse(html)


@router.get("", response_class=HTMLResponse)
async def docs_index(request: Request):
    return _render("index.html", request, title="Inicio", **_common_context("index"))


@router.get("/privacy-policy", response_class=HTMLResponse)
async def docs_privacy_policy(request: Request):
    return _render(
        "privacy-policy.html",
        request,
        title="Politica de privacidad",
        **_common_context("privacy-policy"),
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def docs_endpoint(slug: str, request: Request):
    ep = _ENDPOINT_MAP.get(slug)
    if not ep:
        raise HTTPException(status_code=404, detail="Pagina no encontrada")

    # Prev/next navigation
    idx = ENDPOINTS.index(ep)
    prev_ep = ENDPOINTS[idx - 1] if idx > 0 else None
    next_ep = ENDPOINTS[idx + 1] if idx < len(ENDPOINTS) - 1 else None

    return _render(
        "endpoint.html",
        request,
        title=ep.title,
        endpoint=ep,
        prev_endpoint=prev_ep,
        next_endpoint=next_ep,
        **_common_context(slug),
    )
