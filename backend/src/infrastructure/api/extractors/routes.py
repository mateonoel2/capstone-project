import tempfile
import time
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.logger import get_logger
from src.domain.entities import ExtractorConfigData, UserData
from src.domain.services.extractor_config import ExtractorConfigService

logger = get_logger(__name__)
from src.infrastructure.ai_assist import (
    generate_prompt_from_schema,
    generate_schema_from_description,
    update_prompt_with_instructions,
)
from src.infrastructure.api.extraction.dtos import (
    ExtractorConfigCreateRequest,
    ExtractorConfigListResponse,
    ExtractorConfigResponse,
    ExtractorConfigUpdateRequest,
    ExtractorConfigVersionResponse,
    GeneratePromptRequest,
    GeneratePromptResponse,
    GenerateSchemaRequest,
    GenerateSchemaResponse,
    ModelInfo,
    SetActiveRequest,
    TestExtractionLogResponse,
    TestExtractRequest,
    TestExtractResponse,
    UpdatePromptRequest,
)
from src.infrastructure.auth import UserDep
from src.infrastructure.database import get_db
from src.infrastructure.extractors.statement_extractor import (
    SUPPORTED_EXTENSIONS,
    StatementExtractor,
)
from src.infrastructure.repository import ExtractorConfigRepository, TestExtractionLogRepository
from src.infrastructure.storage import get_storage

DbDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/extractors", tags=["extractors"])

AVAILABLE_MODELS = [
    ModelInfo(
        id="claude-haiku-4-5-20251001",
        name="Claude Haiku 4.5",
        tier="fast",
        cost_hint="$0.80 / $4.00 por 1M tokens",
        is_available=True,
    ),
    ModelInfo(
        id="claude-sonnet-4-6",
        name="Claude Sonnet 4.6",
        tier="balanced",
        cost_hint="$3.00 / $15.00 por 1M tokens",
        is_available=False,
    ),
    ModelInfo(
        id="claude-opus-4-6",
        name="Claude Opus 4.6",
        tier="powerful",
        cost_hint="$15.00 / $75.00 por 1M tokens",
        is_available=False,
    ),
]


def _get_service(db: Session) -> ExtractorConfigService:
    return ExtractorConfigService(ExtractorConfigRepository(db))


def _check_ownership(config: ExtractorConfigData, user: UserData) -> None:
    if user.role != "admin" and config.user_id != user.id:
        raise HTTPException(status_code=404, detail="Extractor config not found")


@router.get("", response_model=ExtractorConfigListResponse)
async def list_extractor_configs(db: DbDep, user: UserDep, status: str | None = None):
    user_filter = None if user.role == "admin" else user.id
    service = _get_service(db)
    configs = service.get_all(status=status, user_id=user_filter)
    return ExtractorConfigListResponse(
        configs=[ExtractorConfigResponse.model_validate(c) for c in configs]
    )


@router.get("/models", response_model=list[ModelInfo])
async def get_available_models(user: UserDep):
    return AVAILABLE_MODELS


@router.post("/generate-schema", response_model=GenerateSchemaResponse)
async def generate_schema(request: GenerateSchemaRequest, user: UserDep):
    try:
        schema = generate_schema_from_description(request.description)
        return GenerateSchemaResponse(output_schema=schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando schema: {str(e)}")


@router.post("/generate-prompt", response_model=GeneratePromptResponse)
async def generate_prompt(request: GeneratePromptRequest, user: UserDep):
    try:
        prompt = generate_prompt_from_schema(request.output_schema, request.document_type)
        return GeneratePromptResponse(prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando prompt: {str(e)}")


@router.post("/update-prompt", response_model=GeneratePromptResponse)
async def update_prompt(request: UpdatePromptRequest, user: UserDep):
    try:
        prompt = update_prompt_with_instructions(
            request.current_prompt, request.instructions, request.output_schema
        )
        return GeneratePromptResponse(prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando prompt: {str(e)}")


@router.post("/test-extract", response_model=TestExtractResponse)
async def test_extract(request: TestExtractRequest, db: DbDep, user: UserDep):
    config_data = request.config
    logger.info("=== Test extract request ===")
    logger.info("Filename: %s, S3 key: %s", request.filename, request.s3_key)
    logger.info("Config keys: %s", list(config_data.keys()))
    logger.info("Extractor config ID: %s", request.extractor_config_id)

    prompt = config_data.get("prompt", "")
    model = config_data.get("model", "claude-haiku-4-5-20251001")
    output_schema = config_data.get("output_schema")

    logger.info("Model: %s", model)
    logger.info("Prompt length: %d, first 200 chars: %.200s", len(prompt), prompt)
    logger.info("Output schema: %s", output_schema)

    if not prompt:
        raise HTTPException(status_code=400, detail="El prompt es requerido")
    if not output_schema:
        raise HTTPException(status_code=400, detail="El schema es requerido")

    valid_model_ids = {m.id for m in AVAILABLE_MODELS}
    if model not in valid_model_ids:
        raise HTTPException(status_code=400, detail=f"Modelo no soportado: {model}")

    if not request.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó un archivo")

    suffix = Path(request.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado: {suffix}",
        )

    test_log_repo = TestExtractionLogRepository(db)
    tmp_path = None
    start = time.monotonic()
    try:
        storage = get_storage()
        file_bytes = storage.download(request.s3_key)

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = Path(tmp.name)

        extractor = StatementExtractor(prompt=prompt, model=model, output_schema=output_schema)
        start = time.monotonic()
        result = extractor.extract_file(tmp_path)
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)

        log = test_log_repo.create(
            filename=request.filename,
            s3_key=request.s3_key,
            prompt_snapshot=prompt,
            model=model,
            output_schema_snapshot=output_schema,
            extracted_fields=result,
            success=True,
            response_time_ms=elapsed_ms,
            extractor_config_id=request.extractor_config_id,
            user_id=user.id,
        )

        return TestExtractResponse(fields=result, response_time_ms=elapsed_ms, test_log_id=log.id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")
    except Exception as e:
        # Log the failed test extraction
        try:
            elapsed_ms = round((time.monotonic() - start) * 1000, 1)
            test_log_repo.create(
                filename=request.filename,
                s3_key=request.s3_key,
                prompt_snapshot=prompt,
                model=model,
                output_schema_snapshot=output_schema or {},
                extracted_fields=None,
                success=False,
                error_message=str(e),
                response_time_ms=elapsed_ms,
                extractor_config_id=request.extractor_config_id,
                user_id=user.id,
            )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


@router.get("/{config_id}/test-logs", response_model=list[TestExtractionLogResponse])
async def get_test_logs(config_id: int, db: DbDep, user: UserDep):
    service = _get_service(db)
    config = service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Extractor config not found")
    _check_ownership(config, user)
    test_log_repo = TestExtractionLogRepository(db)
    logs = test_log_repo.get_by_config_id(config_id)
    return [TestExtractionLogResponse.model_validate(log) for log in logs]


@router.get("/{config_id}", response_model=ExtractorConfigResponse)
async def get_extractor_config(config_id: int, db: DbDep, user: UserDep):
    service = _get_service(db)
    config = service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Extractor config not found")
    _check_ownership(config, user)
    return ExtractorConfigResponse.model_validate(config)


@router.get("/{config_id}/versions", response_model=list[ExtractorConfigVersionResponse])
async def get_extractor_versions(config_id: int, db: DbDep, user: UserDep):
    service = _get_service(db)
    config = service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Extractor config not found")
    _check_ownership(config, user)
    versions = service.get_versions(config_id)
    return [ExtractorConfigVersionResponse.model_validate(v) for v in versions]


@router.post("", response_model=ExtractorConfigResponse, status_code=201)
async def create_extractor_config(request: ExtractorConfigCreateRequest, db: DbDep, user: UserDep):
    service = _get_service(db)
    data = ExtractorConfigData(
        id=None,
        name=request.name,
        description=request.description,
        prompt=request.prompt,
        model=request.model,
        output_schema=request.output_schema,
        is_default=request.is_default,
        status=request.status,
    )
    config = service.create(data, user_id=user.id)
    return ExtractorConfigResponse.model_validate(config)


@router.put("/{config_id}", response_model=ExtractorConfigResponse)
async def update_extractor_config(
    config_id: int, request: ExtractorConfigUpdateRequest, db: DbDep, user: UserDep
):
    service = _get_service(db)
    existing = service.get_by_id(config_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Extractor config not found")
    _check_ownership(existing, user)

    data = ExtractorConfigData(
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
        status=request.status if request.status is not None else existing.status,
    )
    config = service.update(config_id, data)
    return ExtractorConfigResponse.model_validate(config)


@router.delete("/{config_id}")
async def delete_extractor_config(config_id: int, db: DbDep, user: UserDep):
    service = _get_service(db)
    existing = service.get_by_id(config_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Extractor config not found")
    _check_ownership(existing, user)
    if existing.is_default:
        raise HTTPException(status_code=400, detail="No se puede eliminar el extractor por defecto")
    success = service.delete(config_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el extractor")
    return {"message": "Extractor eliminado exitosamente"}


@router.patch(
    "/{config_id}/versions/{version_id}/active",
    response_model=ExtractorConfigVersionResponse,
)
async def toggle_version_active(
    config_id: int, version_id: int, request: SetActiveRequest, db: DbDep, user: UserDep
):
    repo = ExtractorConfigRepository(db)
    config = repo.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Extractor config no encontrado")
    _check_ownership(config, user)

    # Find the version and verify it belongs to this config
    versions = repo.get_versions(config_id)
    version = next((v for v in versions if v.id == version_id), None)
    if not version:
        raise HTTPException(status_code=404, detail="Versión no encontrada para este extractor")

    # If activating, check schema compatibility
    if request.is_active:
        current_keys = sorted(config.output_schema.get("properties", {}).keys())
        version_keys = sorted(version.output_schema.get("properties", {}).keys())
        if current_keys != version_keys:
            raise HTTPException(
                status_code=400,
                detail="El schema de esta versión es incompatible con la configuración actual",
            )

    updated = repo.set_version_active(version_id, request.is_active)
    return ExtractorConfigVersionResponse.model_validate(updated)
