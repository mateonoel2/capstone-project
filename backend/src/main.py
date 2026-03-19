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
from fastapi.responses import JSONResponse

from alembic import command
from src.core.logger import get_logger
from src.infrastructure.api.admin.routes import router as admin_router
from src.infrastructure.api.auth.routes import router as auth_router
from src.infrastructure.api.extraction.routes import router as extraction_router
from src.infrastructure.api.extractors.routes import router as extractors_router
from src.infrastructure.api.tokens.routes import router as tokens_router
from src.infrastructure.storage import get_storage

load_dotenv()

logger = get_logger("api")


def run_migrations():
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    storage = get_storage()
    storage.configure_cors(allowed_origins=["*"])
    yield


app = FastAPI(
    title="Bank Statement Extraction API",
    description="Extract bank account information from PDF statements",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(extraction_router)
app.include_router(extractors_router)
app.include_router(tokens_router)


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
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/")
async def root():
    return {
        "message": "Bank Statement Extraction API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
