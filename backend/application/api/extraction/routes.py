from fastapi import APIRouter, File, HTTPException, UploadFile

from application.api.extraction.dtos import (
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
from application.constants import BANK_DICT_KUSHKI
from application.database import get_session
from application.modules.extraction.entities import SubmissionData
from application.modules.extraction.repository import ExtractionRepository
from application.modules.extraction.service import ExtractionService

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post("/pdf", response_model=ExtractionResponse)
async def extract_from_pdf(file: UploadFile = File(...)):
    session = None
    try:
        session = get_session()
        repository = ExtractionRepository(session)
        service = ExtractionService(repository)

        result = await service.extract_from_pdf(file)

        return ExtractionResponse(
            owner=result.owner,
            bank_name=result.bank_name,
            account_number=result.account_number,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        if session:
            session.close()


@router.post("/submit", response_model=SubmissionResponse)
async def submit_extraction(submission: SubmissionRequest):
    session = None
    try:
        session = get_session()
        repository = ExtractionRepository(session)
        service = ExtractionService(repository)

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
        if session:
            session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record submission: {str(e)}")
    finally:
        if session:
            session.close()


@router.get("/banks", response_model=BanksResponse)
async def get_banks():
    banks = [Bank(name=name, code=code) for name, code in BANK_DICT_KUSHKI.items()]
    return BanksResponse(banks=sorted(banks, key=lambda x: x.name))


@router.get("/logs", response_model=LogsResponse)
async def get_extraction_logs(page: int = 1, page_size: int = 50):
    session = None
    try:
        session = get_session()
        repository = ExtractionRepository(session)
        service = ExtractionService(repository)

        logs, total, total_pages = service.get_extraction_logs(page, page_size)

        logs_data = [
            ExtractionLogResponse(
                id=log.id,
                timestamp=log.timestamp.isoformat() if log.timestamp else None,
                filename=log.filename,
                extracted_owner=log.extracted_owner,
                extracted_bank_name=log.extracted_bank_name,
                extracted_account_number=log.extracted_account_number,
                final_owner=log.final_owner,
                final_bank_name=log.final_bank_name,
                final_account_number=log.final_account_number,
                owner_corrected=log.owner_corrected,
                bank_name_corrected=log.bank_name_corrected,
                account_number_corrected=log.account_number_corrected,
            )
            for log in logs
        ]

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
    finally:
        if session:
            session.close()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    session = None
    try:
        session = get_session()
        repository = ExtractionRepository(session)
        service = ExtractionService(repository)

        metrics = service.get_metrics()

        return MetricsResponse(
            total_extractions=metrics.total_extractions,
            total_corrections=metrics.total_corrections,
            accuracy_rate=metrics.accuracy_rate,
            this_week=metrics.this_week,
            owner_accuracy=metrics.owner_accuracy,
            bank_name_accuracy=metrics.bank_name_accuracy,
            account_number_accuracy=metrics.account_number_accuracy,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")
    finally:
        if session:
            session.close()

