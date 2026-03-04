import sys
from contextlib import asynccontextmanager
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from alembic import command
from alembic.config import Config

from src.infrastructure.api.extraction.routes import router as extraction_router

load_dotenv()


def run_migrations():
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
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

app.include_router(extraction_router)


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
