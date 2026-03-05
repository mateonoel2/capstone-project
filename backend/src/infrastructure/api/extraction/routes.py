from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.domain.constants import BANK_DICT_KUSHKI, UNKNOWN_ACCOUNT, UNKNOWN_OWNER
from src.domain.entities import ExtractionError, SubmissionData
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
from src.infrastructure.repository import ApiCallRepository, ExtractionRepository

DbDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/extraction", tags=["extraction"])


def _get_repository(db: Session) -> ExtractionRepository:
    return ExtractionRepository(db)


@router.post("/extract", response_model=ExtractionResponse)
async def extract_from_file(
    file: Annotated[UploadFile, File()],
    db: DbDep,
):
    api_repo = ApiCallRepository(db)
    try:
        content = await file.read()
        await file.seek(0)

        from src.infrastructure.storage import save_upload

        save_upload(file, content)

        service = ExtractionService()
        result, call_result = await service.extract(file)

        api_repo.create(call_result, filename=file.filename)

        return ExtractionResponse(
            owner="" if result.owner == UNKNOWN_OWNER else result.owner,
            bank_name="" if result.bank_name == UNKNOWN_OWNER else result.bank_name,
            account_number=""
            if result.account_number == UNKNOWN_ACCOUNT
            else result.account_number,
        )
    except ExtractionError as e:
        api_repo.create(e.call_result, filename=file.filename)
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
            extracted_owner=submission.extracted_owner,
            extracted_bank_name=submission.extracted_bank_name,
            extracted_account_number=submission.extracted_account_number,
            final_owner=submission.final_owner,
            final_bank_name=submission.final_bank_name,
            final_account_number=submission.final_account_number,
        )

        log_id = service.submit_extraction(submission_data)

        return SubmissionResponse(message="Submission recorded successfully", id=log_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record submission: {str(e)}")


@router.get("/banks", response_model=BanksResponse)
async def get_banks():
    banks = [Bank(name=name, code=code) for name, code in BANK_DICT_KUSHKI.items()]
    return BanksResponse(banks=sorted(banks, key=lambda x: x.name))


@router.get("/logs", response_model=LogsResponse)
async def get_extraction_logs(db: DbDep, page: int = 1, page_size: int = 50):
    try:
        service = SubmissionService(_get_repository(db))
        logs, total, total_pages = service.get_extraction_logs(page, page_size)

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
async def get_metrics(db: DbDep):
    try:
        service = MetricsService(_get_repository(db))
        metrics = service.get_metrics()

        return MetricsResponse.model_validate(metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@router.get("/api-metrics", response_model=ApiCallMetricsResponse)
async def get_api_metrics(db: DbDep):
    try:
        service = ApiMetricsService(ApiCallRepository(db))
        metrics = service.get_metrics()

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
