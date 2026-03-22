import copy
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from alembic import command
from src.core.logger import get_logger
from src.domain.entities import QuotaExceededError
from src.infrastructure.api.admin.routes import router as admin_router
from src.infrastructure.api.auth.routes import router as auth_router
from src.infrastructure.api.extraction.routes import router as extraction_router
from src.infrastructure.api.extractors.routes import router as extractors_router
from src.infrastructure.api.privacy.routes import router as privacy_router
from src.infrastructure.api.tokens.routes import router as tokens_router
from src.infrastructure.storage import get_storage

load_dotenv()

logger = get_logger("api")


def run_migrations():
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    command.upgrade(alembic_cfg, "head")


def _get_allowed_origins() -> list[str]:
    origins = os.getenv("ALLOWED_ORIGINS", "")
    if origins:
        return [o.strip() for o in origins.split(",") if o.strip()]
    return ["http://localhost:3000"]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses (HSTS, CSP, X-Content-Type-Options, etc.)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    storage = get_storage()
    allowed = _get_allowed_origins()
    storage.configure_cors(allowed_origins=allowed)
    yield


app = FastAPI(
    title="Extracto API",
    description="API de extracción de documentos",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(extraction_router)
app.include_router(extractors_router)
app.include_router(tokens_router)
app.include_router(privacy_router)


AUDITED_PATHS = {"/extraction/extract", "/extraction/submit", "/extraction/logs", "/admin/users"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    logger.info(
        "%s %s → %d (%.0fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )

    # Audit log for sensitive data access
    path = request.url.path
    if any(path.startswith(p) for p in AUDITED_PATHS) and response.status_code < 400:
        try:
            from src.infrastructure.database import SessionLocal
            from src.infrastructure.repository import AuditLogRepository

            db = SessionLocal()
            try:
                user_id = None
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    import jwt as pyjwt

                    from src.infrastructure.auth import JWT_ALGORITHM, JWT_SECRET

                    token = auth_header[7:]
                    if not token.startswith("exto_"):
                        try:
                            payload = pyjwt.decode(
                                token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
                            )
                            user_id = payload.get("user_id")
                        except Exception:
                            pass

                ip = request.client.host if request.client else None
                AuditLogRepository(db).create(
                    action=f"{request.method} {path}",
                    resource_type="api_access",
                    user_id=user_id,
                    ip_address=ip,
                )
            finally:
                db.close()
        except Exception:
            pass  # Never block requests due to audit failures

    return response


@app.exception_handler(QuotaExceededError)
async def quota_exceeded_handler(request: Request, exc: QuotaExceededError):
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


CLIENT_ENDPOINT_WHITELIST = {
    ("POST", "/extraction/upload-url"),
    ("POST", "/extraction/upload"),
    ("POST", "/extraction/extract"),
    ("POST", "/extraction/submit"),
    ("GET", "/extraction/banks"),
    ("GET", "/extractors"),
    ("GET", "/extractors/models"),
    ("GET", "/extractors/{config_id}"),
    ("GET", "/extractors/{config_id}/versions"),
    ("GET", "/tokens"),
    ("POST", "/tokens"),
    ("DELETE", "/tokens/{token_id}"),
}


def _collect_refs(obj: dict | list) -> set[str]:
    """Recursively collect all $ref schema names from an OpenAPI structure."""
    refs: set[str] = set()
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref = obj["$ref"]
            if ref.startswith("#/components/schemas/"):
                refs.add(ref.split("/")[-1])
        for v in obj.values():
            refs |= _collect_refs(v)
    elif isinstance(obj, list):
        for item in obj:
            refs |= _collect_refs(item)
    return refs


def get_client_openapi_schema() -> dict:
    """Return a filtered OpenAPI spec containing only client-facing endpoints."""
    full = app.openapi()
    spec = copy.deepcopy(full)

    spec["info"] = {
        "title": "Extracto Client API",
        "description": (
            "API para integración programática con Extracto.\n\n"
            "**Autenticación:** header `Authorization: Bearer <api_token>`.\n\n"
            "**Métricas:** las extracciones realizadas vía API se registran en el "
            "dashboard del usuario dueño del token, igual que las extracciones "
            "hechas desde la interfaz web."
        ),
        "version": spec["info"].get("version", "1.0.0"),
    }

    filtered_paths: dict = {}
    for path, methods in spec.get("paths", {}).items():
        filtered_methods: dict = {}
        for method, operation in methods.items():
            if method.upper() == "OPTIONS":
                continue
            if (method.upper(), path) in CLIENT_ENDPOINT_WHITELIST:
                filtered_methods[method] = operation
        if filtered_methods:
            filtered_paths[path] = filtered_methods
    spec["paths"] = filtered_paths

    # Prune unused schemas
    used_refs = _collect_refs(filtered_paths)
    # Resolve transitively
    schemas = spec.get("components", {}).get("schemas", {})
    resolved: set[str] = set()
    queue = list(used_refs)
    while queue:
        name = queue.pop()
        if name in resolved:
            continue
        resolved.add(name)
        if name in schemas:
            for dep in _collect_refs(schemas[name]):
                if dep not in resolved:
                    queue.append(dep)
    spec.setdefault("components", {})["schemas"] = {
        k: v for k, v in schemas.items() if k in resolved
    }

    return spec


@app.get("/api/openapi.json", include_in_schema=False)
async def client_openapi():
    return JSONResponse(get_client_openapi_schema())


@app.get("/api/docs", include_in_schema=False, response_class=HTMLResponse)
async def client_docs():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="Extracto Client API",
    )


@app.get("/")
async def root():
    return {
        "message": "Extracto API",
        "docs": "/docs",
        "client_docs": "/api/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
