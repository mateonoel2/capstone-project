from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.domain.constants import BANK_DICT_KUSHKI
from src.domain.entities import ExtractionError, ParserConfigData, SubmissionData
from src.domain.services.api_metrics import ApiMetricsService
from src.domain.services.extraction import ExtractionService
from src.domain.services.metrics import MetricsService
from src.domain.services.submission import SubmissionService
from src.infrastructure.api.extraction.dtos import (
    ABTestResponse,
    ABTestResultItem,
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
from src.infrastructure.repository import (
    ApiCallRepository,
    ExtractionRepository,
    ParserConfigRepository,
)

DbDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/extraction", tags=["extraction"])


def _get_repository(db: Session) -> ExtractionRepository:
    return ExtractionRepository(db)


def _load_config(db: Session, config_id: int | None) -> ParserConfigData | None:
    if config_id is None:
        return None
    repo = ParserConfigRepository(db)
    config = repo.get_by_id(config_id)
    if not config:
        return None
    return ParserConfigData(
        id=config.id,
        name=config.name,
        description=config.description or "",
        prompt=config.prompt,
        model=config.model,
        output_schema=config.output_schema,
        is_default=config.is_default,
    )


@router.post("/extract", response_model=ExtractionResponse)
async def extract_from_file(
    file: Annotated[UploadFile, File()],
    db: DbDep,
    parser_config_id: Annotated[int | None, Form()] = None,
):
    api_repo = ApiCallRepository(db)
    config_data = _load_config(db, parser_config_id)

    try:
        content = await file.read()
        await file.seek(0)

        from src.infrastructure.storage import save_upload

        save_upload(file, content)

        service = ExtractionService()
        result, call_result, _ = await service.extract(file, config=config_data)

        api_repo.create(call_result, filename=file.filename)

        # Determine parser config info for the response
        if config_data:
            pc_id = config_data.id
            pc_name = config_data.name
        else:
            pc_repo = ParserConfigRepository(db)
            default_config = pc_repo.get_default()
            pc_id = default_config.id if default_config else None
            pc_name = default_config.name if default_config else "Default"

        return ExtractionResponse(
            fields=result,
            parser_config_id=pc_id,
            parser_config_name=pc_name,
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


@router.post("/ab-test", response_model=ABTestResponse)
async def ab_test(
    file: Annotated[UploadFile, File()],
    config_ids: Annotated[str, Form()],
    db: DbDep,
):
    try:
        ids = [int(x.strip()) for x in config_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400, detail="config_ids debe ser una lista de IDs separados por comas"
        )

    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="Se necesitan al menos 2 configs para A/B test")
    if len(ids) > 4:
        raise HTTPException(status_code=400, detail="Máximo 4 configs para A/B test")

    # Read file content once
    content = await file.read()

    api_repo = ApiCallRepository(db)
    results: list[ABTestResultItem] = []

    import tempfile
    import time
    from pathlib import Path

    from src.domain.entities import ApiCallResult
    from src.domain.services.extraction import (
        _create_parser,
        apply_bank_statement_postprocessing,
    )

    suffix = Path(file.filename).suffix.lower() if file.filename else ".pdf"

    for config_id in ids:
        config_data = _load_config(db, config_id)
        if not config_data:
            results.append(
                ABTestResultItem(
                    parser_config_id=config_id,
                    parser_config_name="Unknown",
                    model="",
                    fields={},
                    response_time_ms=0,
                    success=False,
                    error=f"Config {config_id} not found",
                )
            )
            continue

        tmp_file_path = None
        start = time.monotonic()

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_file_path = Path(tmp.name)

            parser = _create_parser(config_data)
            start = time.monotonic()
            raw_result = parser.parse_file(tmp_file_path)
            elapsed_ms = round((time.monotonic() - start) * 1000, 1)

            if config_data.is_default:
                raw_result = apply_bank_statement_postprocessing(raw_result)

            call_result = ApiCallResult(
                model=parser.model_name,
                success=True,
                response_time_ms=elapsed_ms,
            )
            api_repo.create(call_result, filename=file.filename)

            results.append(
                ABTestResultItem(
                    parser_config_id=config_id,
                    parser_config_name=config_data.name,
                    model=config_data.model,
                    fields=raw_result,
                    response_time_ms=elapsed_ms,
                    success=True,
                )
            )
        except Exception as e:
            elapsed_ms = round((time.monotonic() - start) * 1000, 1)
            call_result = ApiCallResult(
                model=config_data.model,
                success=False,
                response_time_ms=elapsed_ms,
                error_type=type(e).__name__,
                error_message=str(e)[:500],
            )
            api_repo.create(call_result, filename=file.filename)
            results.append(
                ABTestResultItem(
                    parser_config_id=config_id,
                    parser_config_name=config_data.name,
                    model=config_data.model,
                    fields={},
                    response_time_ms=elapsed_ms,
                    success=False,
                    error=str(e)[:500],
                )
            )
        finally:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()

    return ABTestResponse(results=results)


@router.post("/submit", response_model=SubmissionResponse)
async def submit_extraction(submission: SubmissionRequest, db: DbDep):
    try:
        service = SubmissionService(_get_repository(db))

        submission_data = SubmissionData(
            filename=submission.filename,
            extracted_fields=submission.extracted_fields,
            final_fields=submission.final_fields,
        )

        log_id = service.submit_extraction(submission_data, submission.parser_config_id)

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
async def get_metrics(db: DbDep, parser_config_id: int | None = None):
    try:
        service = MetricsService(_get_repository(db))
        metrics = service.get_metrics(parser_config_id=parser_config_id)

        return MetricsResponse.model_validate(metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@router.get("/api-metrics", response_model=ApiCallMetricsResponse)
async def get_api_metrics(db: DbDep, parser_config_id: int | None = None):
    try:
        service = ApiMetricsService(ApiCallRepository(db))
        metrics = service.get_metrics(parser_config_id=parser_config_id)

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
