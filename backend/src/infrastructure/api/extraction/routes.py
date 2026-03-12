import random
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.domain.constants import BANK_DICT_KUSHKI
from src.domain.entities import ExtractionError, ExtractorConfigData, SubmissionData
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
    LogsResponse,
    MetricsResponse,
    PaginationMeta,
    SubmissionRequest,
    SubmissionResponse,
)
from src.infrastructure.database import get_db
from src.infrastructure.models import ExtractorConfigVersion
from src.infrastructure.repository import (
    ApiCallRepository,
    ExtractionRepository,
    ExtractorConfigRepository,
)

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
        return None
    return ExtractorConfigData(
        id=config.id,
        name=config.name,
        description=config.description or "",
        prompt=config.prompt,
        model=config.model,
        output_schema=config.output_schema,
        is_default=config.is_default,
    )


def _select_variant(
    config: ExtractorConfigData, active_versions: list[ExtractorConfigVersion]
) -> tuple[ExtractorConfigData, int | None, int | None]:
    """Pick a variant randomly from current config + active versions.

    Returns (config_to_use, version_id, version_number).
    version_id=None means the current config was selected.
    """
    if not active_versions:
        return config, None, None

    # Build list: None = current config, or a version object
    candidates: list[ExtractorConfigVersion | None] = [None] + list(active_versions)
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


@router.post("/extract", response_model=ExtractionResponse)
async def extract_from_file(
    file: Annotated[UploadFile, File()],
    db: DbDep,
    extractor_config_id: Annotated[int | None, Form()] = None,
):
    api_repo = ApiCallRepository(db)
    config_data = _load_config(db, extractor_config_id)

    # Select A/B variant if active versions exist
    version_id = None
    version_number = None
    if config_data and config_data.id is not None:
        ec_repo = ExtractorConfigRepository(db)
        active_versions = ec_repo.get_active_versions(config_data.id)
        config_data, version_id, version_number = _select_variant(config_data, active_versions)

    try:
        content = await file.read()
        await file.seek(0)

        from src.infrastructure.storage import save_upload

        save_upload(file, content)

        service = ExtractionService()
        result, call_result, _ = await service.extract(file, config=config_data)

        api_repo.create(
            call_result,
            filename=file.filename,
            extractor_config_id=extractor_config_id,
            extractor_config_version_id=version_id,
        )

        # Determine extractor config info for the response
        if config_data:
            ec_id = extractor_config_id or config_data.id
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
            filename=file.filename,
            extractor_config_id=extractor_config_id,
            extractor_config_version_id=version_id,
        )
        if e.call_result.error_type == "InvalidDocument":
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/submit", response_model=SubmissionResponse)
async def submit_extraction(submission: SubmissionRequest, db: DbDep):
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
    db: DbDep, page: int = 1, page_size: int = 50, extractor_config_id: int | None = None
):
    try:
        service = SubmissionService(_get_repository(db))
        logs, total, total_pages = service.get_extraction_logs(page, page_size, extractor_config_id)

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
async def get_metrics(db: DbDep, extractor_config_id: int | None = None):
    try:
        service = MetricsService(_get_repository(db))
        metrics = service.get_metrics(extractor_config_id=extractor_config_id)

        return MetricsResponse.model_validate(metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@router.get("/api-metrics", response_model=ApiCallMetricsResponse)
async def get_api_metrics(db: DbDep, extractor_config_id: int | None = None):
    try:
        service = ApiMetricsService(ApiCallRepository(db))
        metrics = service.get_metrics(extractor_config_id=extractor_config_id)

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
