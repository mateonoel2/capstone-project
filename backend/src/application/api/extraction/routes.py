from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.application.api.extraction.dtos import (
    Bank,
    BanksResponse,
    ExtractionLogResponse,
    ExtractionResponse,
    LogsResponse,
    MetricsResponse,
    PaginationMeta,
    SubmissionRequest,
    SubmissionResponse,
)
from src.application.database import get_db
from src.application.modules.extraction.entities import SubmissionData
from src.application.modules.extraction.repository import ExtractionRepository
from src.application.modules.extraction.service import (
    ExtractionService,
    MetricsService,
    SubmissionService,
)
from src.constants import BANK_DICT_KUSHKI, UNKNOWN_ACCOUNT, UNKNOWN_OWNER

DbDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/extraction", tags=["extraction"])


def _get_repository(db: Session) -> ExtractionRepository:
    return ExtractionRepository(db)


@router.post("/pdf", response_model=ExtractionResponse)
async def extract_from_pdf(
    file: Annotated[UploadFile, File()],
    parser: Annotated[str, Form()] = "claude_ocr",
):
    try:
        service = ExtractionService()
        result = await service.extract_from_pdf(file, parser)

        return ExtractionResponse(
            owner="" if result.owner == UNKNOWN_OWNER else result.owner,
            bank_name="" if result.bank_name == UNKNOWN_OWNER else result.bank_name,
            account_number=""
            if result.account_number == UNKNOWN_ACCOUNT
            else result.account_number,
        )
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
