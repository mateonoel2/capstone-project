import random
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.domain.constants import BANK_DICT_KUSHKI
from src.domain.entities import (
    ExtractionError,
    ExtractorConfigData,
    ExtractorConfigVersionData,
    SubmissionData,
)
from src.domain.services.api_metrics import ApiMetricsService
from src.domain.services.extraction import ExtractionService
from src.domain.services.metrics import MetricsService
from src.domain.services.submission import SubmissionService
from src.infrastructure.api.extraction.dtos import (
    ApiCallMetricsResponse,
    Bank,
    BanksResponse,
    ErrorBreakdownItem,
    ExtractionLogResponse,
    ExtractionResponse,
    ExtractRequest,
    LogsResponse,
    MetricsResponse,
    PaginationMeta,
    SubmissionRequest,
    SubmissionResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from src.infrastructure.auth import UserDep
from src.infrastructure.database import get_db
from src.infrastructure.repository import (
    ApiCallRepository,
    ExtractionRepository,
    ExtractorConfigRepository,
)
from src.infrastructure.storage import generate_key, get_storage

DbDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/extraction", tags=["extraction"])


def _get_repository(db: Session) -> ExtractionRepository:
    return ExtractionRepository(db)


def _load_config(db: Session, config_id: int | None) -> ExtractorConfigData | None:
    if config_id is None:
        return None
    repo = ExtractorConfigRepository(db)
    config = repo.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Extractor config {config_id} no encontrado")
    return config


def _select_variant(
    config: ExtractorConfigData, active_versions: list[ExtractorConfigVersionData]
) -> tuple[ExtractorConfigData, int | None, int | None]:
    """Pick a variant randomly from current config + active versions.

    Returns (config_to_use, version_id, version_number).
    version_id=None means the current config was selected.
    """
    if not active_versions:
        return config, None, None

    # Build list: None = current config, or a version object
    candidates: list[ExtractorConfigVersionData | None] = [None] + list(active_versions)
    chosen = random.choice(candidates)

    if chosen is None:
        return config, None, None

    version_config = ExtractorConfigData(
        id=config.id,
        name=config.name,
        description=config.description,
        prompt=chosen.prompt,
        model=chosen.model,
        output_schema=chosen.output_schema,
        is_default=config.is_default,
    )
    return version_config, chosen.id, chosen.version_number


@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(request: UploadUrlRequest, user: UserDep):
    """Return an S3 key and presigned upload URL (None when S3 is not configured)."""
    if not request.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó un nombre de archivo")
    storage = get_storage()
    key = generate_key(request.filename)
    upload_url = storage.generate_upload_url(key, request.content_type)
    return UploadUrlResponse(s3_key=key, upload_url=upload_url, filename=request.filename)


@router.post("/upload")
async def upload_file(file: Annotated[UploadFile, File()], user: UserDep):
    """Fallback upload through backend (used when S3 presigned URLs are not available)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó un archivo")
    storage = get_storage()
    key = generate_key(file.filename)
    content = await file.read()
    storage.save(key, content)
    return UploadUrlResponse(s3_key=key, upload_url=None, filename=file.filename)


@router.post("/extract", response_model=ExtractionResponse)
async def extract_from_file(request: ExtractRequest, db: DbDep, user: UserDep):
    api_repo = ApiCallRepository(db)
    config_data = _load_config(db, request.extractor_config_id)

    # Select A/B variant if active versions exist
    version_id = None
    version_number = None
    if config_data and config_data.id is not None:
        ec_repo = ExtractorConfigRepository(db)
        active_versions = ec_repo.get_active_versions(config_data.id)
        config_data, version_id, version_number = _select_variant(config_data, active_versions)

    try:
        storage = get_storage()
        file_bytes = storage.download(request.s3_key)

        service = ExtractionService()
        result, call_result, _ = service.extract(file_bytes, request.filename, config=config_data)

        api_repo.create(
            call_result,
            filename=request.filename,
            extractor_config_id=request.extractor_config_id,
            extractor_config_version_id=version_id,
            user_id=user.id,
        )

        # Determine extractor config info for the response
        if config_data:
            ec_id = request.extractor_config_id or config_data.id
            ec_name = config_data.name
        else:
            ec_repo = ExtractorConfigRepository(db)
            default_config = ec_repo.get_default()
            ec_id = default_config.id if default_config else None
            ec_name = default_config.name if default_config else "Default"

        return ExtractionResponse(
            fields=result,
            extractor_config_id=ec_id,
            extractor_config_name=ec_name,
            extractor_config_version_id=version_id,
            extractor_config_version_number=version_number,
        )
    except ExtractionError as e:
        api_repo.create(
            e.call_result,
            filename=request.filename,
            extractor_config_id=request.extractor_config_id,
            extractor_config_version_id=version_id,
            user_id=user.id,
        )
        if e.call_result.error_type == "InvalidDocument":
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado en storage")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/submit", response_model=SubmissionResponse)
async def submit_extraction(submission: SubmissionRequest, db: DbDep, user: UserDep):
    try:
        service = SubmissionService(_get_repository(db))

        submission_data = SubmissionData(
            filename=submission.filename,
            extracted_fields=submission.extracted_fields,
            final_fields=submission.final_fields,
        )

        log_id = service.submit_extraction(
            submission_data,
            submission.extractor_config_id,
            submission.extractor_config_version_id,
            user_id=user.id,
        )

        return SubmissionResponse(message="Submission recorded successfully", id=log_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record submission: {str(e)}")


@router.get("/banks", response_model=BanksResponse)
async def get_banks():
    banks = [Bank(name=name, code=code) for name, code in BANK_DICT_KUSHKI.items()]
    return BanksResponse(banks=sorted(banks, key=lambda x: x.name))


@router.get("/logs", response_model=LogsResponse)
async def get_extraction_logs(
    db: DbDep,
    user: UserDep,
    page: int = 1,
    page_size: int = 50,
    extractor_config_id: int | None = None,
):
    try:
        user_filter = None if user.role == "admin" else user.id
        service = SubmissionService(_get_repository(db))
        logs, total, total_pages = service.get_extraction_logs(
            page, page_size, extractor_config_id, user_id=user_filter
        )

        logs_data = [ExtractionLogResponse.model_validate(log) for log in logs]

        return LogsResponse(
            logs=logs_data,
            pagination=PaginationMeta(
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db: DbDep, user: UserDep, extractor_config_id: int | None = None):
    try:
        user_filter = None if user.role == "admin" else user.id
        service = MetricsService(_get_repository(db))
        metrics = service.get_metrics(extractor_config_id=extractor_config_id, user_id=user_filter)

        return MetricsResponse.model_validate(metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@router.get("/api-metrics", response_model=ApiCallMetricsResponse)
async def get_api_metrics(db: DbDep, user: UserDep, extractor_config_id: int | None = None):
    try:
        user_filter = None if user.role == "admin" else user.id
        service = ApiMetricsService(ApiCallRepository(db))
        metrics = service.get_metrics(extractor_config_id=extractor_config_id, user_id=user_filter)

        return ApiCallMetricsResponse(
            total_calls=metrics.total_calls,
            total_failures=metrics.total_failures,
            error_rate=metrics.error_rate,
            avg_response_time_ms=metrics.avg_response_time_ms,
            calls_this_week=metrics.calls_this_week,
            error_breakdown=[
                ErrorBreakdownItem(error_type=str(item["error_type"]), count=int(item["count"]))
                for item in metrics.error_breakdown
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate API metrics: {str(e)}")
