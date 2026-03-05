from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.domain.entities import ParserConfigData
from src.domain.services.parser_config import ParserConfigService
from src.infrastructure.api.extraction.dtos import (
    ModelInfo,
    ParserConfigCreateRequest,
    ParserConfigListResponse,
    ParserConfigResponse,
    ParserConfigUpdateRequest,
    ParserConfigVersionResponse,
)
from src.infrastructure.database import get_db
from src.infrastructure.repository import ParserConfigRepository

DbDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/parsers", tags=["parsers"])

AVAILABLE_MODELS = [
    ModelInfo(
        id="claude-haiku-4-5-20251001",
        name="Claude Haiku 4.5",
        tier="fast",
        cost_hint="$0.80 / $4.00 por 1M tokens",
    ),
    ModelInfo(
        id="claude-sonnet-4-6",
        name="Claude Sonnet 4.6",
        tier="balanced",
        cost_hint="$3.00 / $15.00 por 1M tokens",
    ),
    ModelInfo(
        id="claude-opus-4-6",
        name="Claude Opus 4.6",
        tier="powerful",
        cost_hint="$15.00 / $75.00 por 1M tokens",
    ),
]


def _get_service(db: Session) -> ParserConfigService:
    return ParserConfigService(ParserConfigRepository(db))


@router.get("", response_model=ParserConfigListResponse)
async def list_parser_configs(db: DbDep):
    service = _get_service(db)
    configs = service.get_all()
    return ParserConfigListResponse(
        configs=[ParserConfigResponse.model_validate(c) for c in configs]
    )


@router.get("/models", response_model=list[ModelInfo])
async def get_available_models():
    return AVAILABLE_MODELS


@router.get("/{config_id}", response_model=ParserConfigResponse)
async def get_parser_config(config_id: int, db: DbDep):
    service = _get_service(db)
    config = service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Parser config not found")
    return ParserConfigResponse.model_validate(config)


@router.get("/{config_id}/versions", response_model=list[ParserConfigVersionResponse])
async def get_parser_versions(config_id: int, db: DbDep):
    service = _get_service(db)
    config = service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Parser config not found")
    versions = service.get_versions(config_id)
    return [ParserConfigVersionResponse.model_validate(v) for v in versions]


@router.post("", response_model=ParserConfigResponse, status_code=201)
async def create_parser_config(request: ParserConfigCreateRequest, db: DbDep):
    service = _get_service(db)
    data = ParserConfigData(
        id=None,
        name=request.name,
        description=request.description,
        prompt=request.prompt,
        model=request.model,
        output_schema=request.output_schema,
        is_default=request.is_default,
    )
    config = service.create(data)
    return ParserConfigResponse.model_validate(config)


@router.put("/{config_id}", response_model=ParserConfigResponse)
async def update_parser_config(config_id: int, request: ParserConfigUpdateRequest, db: DbDep):
    service = _get_service(db)
    existing = service.get_by_id(config_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Parser config not found")

    data = ParserConfigData(
        id=config_id,
        name=request.name if request.name is not None else existing.name,
        description=request.description
        if request.description is not None
        else (existing.description or ""),
        prompt=request.prompt if request.prompt is not None else existing.prompt,
        model=request.model if request.model is not None else existing.model,
        output_schema=request.output_schema
        if request.output_schema is not None
        else existing.output_schema,
        is_default=request.is_default if request.is_default is not None else existing.is_default,
    )
    config = service.update(config_id, data)
    return ParserConfigResponse.model_validate(config)


@router.delete("/{config_id}")
async def delete_parser_config(config_id: int, db: DbDep):
    service = _get_service(db)
    existing = service.get_by_id(config_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Parser config not found")
    if existing.is_default:
        raise HTTPException(status_code=400, detail="No se puede eliminar el parser por defecto")
    success = service.delete(config_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el parser")
    return {"message": "Parser eliminado exitosamente"}
