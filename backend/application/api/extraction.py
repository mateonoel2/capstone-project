import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func

from application.constants import BANK_DICT_KUSHKI
from application.database import ExtractionLog, get_session
from src.extraction.claude_ocr_parser import ClaudeOCRParser

router = APIRouter(prefix="/extraction", tags=["extraction"])


class ExtractionResponse(BaseModel):
    owner: str
    bank_name: str
    account_number: str


class SubmissionRequest(BaseModel):
    filename: str
    extracted_owner: str
    extracted_bank_name: str
    extracted_account_number: str
    final_owner: str
    final_bank_name: str
    final_account_number: str


@router.post("/pdf", response_model=ExtractionResponse)
async def extract_from_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = Path(tmp_file.name)

        parser = ClaudeOCRParser()
        result = parser.parse_file(tmp_file_path)

        tmp_file_path.unlink()

        return ExtractionResponse(
            owner="" if result.owner == "Unknown" else result.owner,
            bank_name="" if result.bank_name == "Unknown" else result.bank_name,
            account_number=""
            if result.account_number == "000000000000000000"
            else result.account_number,
        )

    except Exception as e:
        if tmp_file_path.exists():
            tmp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/submit")
async def submit_extraction(submission: SubmissionRequest):
    session = None
    try:
        session = get_session()

        log_entry = ExtractionLog(
            filename=submission.filename,
            extracted_owner=submission.extracted_owner,
            extracted_bank_name=submission.extracted_bank_name,
            extracted_account_number=submission.extracted_account_number,
            final_owner=submission.final_owner,
            final_bank_name=submission.final_bank_name,
            final_account_number=submission.final_account_number,
            owner_corrected=submission.extracted_owner != submission.final_owner,
            bank_name_corrected=submission.extracted_bank_name != submission.final_bank_name,
            account_number_corrected=submission.extracted_account_number
            != submission.final_account_number,
        )

        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        entry_id = log_entry.id

        return {"message": "Submission recorded successfully", "id": entry_id}

    except Exception as e:
        if session:
            session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record submission: {str(e)}")
    finally:
        if session:
            session.close()


@router.get("/banks")
async def get_banks():
    banks = [{"name": name, "code": code} for name, code in BANK_DICT_KUSHKI.items()]
    return {"banks": sorted(banks, key=lambda x: x["name"])}


@router.get("/logs")
async def get_extraction_logs():
    session = None
    try:
        session = get_session()
        logs = session.query(ExtractionLog).order_by(ExtractionLog.timestamp.desc()).all()

        logs_data = [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "filename": log.filename,
                "extracted_owner": log.extracted_owner,
                "extracted_bank_name": log.extracted_bank_name,
                "extracted_account_number": log.extracted_account_number,
                "final_owner": log.final_owner,
                "final_bank_name": log.final_bank_name,
                "final_account_number": log.final_account_number,
                "owner_corrected": log.owner_corrected,
                "bank_name_corrected": log.bank_name_corrected,
                "account_number_corrected": log.account_number_corrected,
            }
            for log in logs
        ]

        return {"logs": logs_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")
    finally:
        if session:
            session.close()


@router.get("/metrics")
async def get_metrics():
    session = None
    try:
        session = get_session()

        total_extractions = session.query(func.count(ExtractionLog.id)).scalar() or 0

        if total_extractions == 0:
            return {
                "total_extractions": 0,
                "total_corrections": 0,
                "accuracy_rate": 0.0,
                "this_week": 0,
                "owner_accuracy": 0.0,
                "bank_name_accuracy": 0.0,
                "account_number_accuracy": 0.0,
            }

        total_owner_corrections = (
            session.query(func.count(ExtractionLog.id))
            .filter(ExtractionLog.owner_corrected)
            .scalar()
            or 0
        )

        total_bank_corrections = (
            session.query(func.count(ExtractionLog.id))
            .filter(ExtractionLog.bank_name_corrected)
            .scalar()
            or 0
        )

        total_account_corrections = (
            session.query(func.count(ExtractionLog.id))
            .filter(ExtractionLog.account_number_corrected)
            .scalar()
            or 0
        )

        logs_with_any_correction = (
            session.query(func.count(ExtractionLog.id))
            .filter(
                (ExtractionLog.owner_corrected)
                | (ExtractionLog.bank_name_corrected)
                | (ExtractionLog.account_number_corrected)
            )
            .scalar()
            or 0
        )

        week_ago = datetime.utcnow() - timedelta(days=7)
        this_week_count = (
            session.query(func.count(ExtractionLog.id))
            .filter(ExtractionLog.timestamp >= week_ago)
            .scalar()
            or 0
        )

        total_fields = total_extractions * 3
        total_field_corrections = (
            total_owner_corrections + total_bank_corrections + total_account_corrections
        )
        accuracy_rate = (
            ((total_fields - total_field_corrections) / total_fields * 100)
            if total_fields > 0
            else 0.0
        )

        owner_accuracy = (
            ((total_extractions - total_owner_corrections) / total_extractions * 100)
            if total_extractions > 0
            else 0.0
        )
        bank_name_accuracy = (
            ((total_extractions - total_bank_corrections) / total_extractions * 100)
            if total_extractions > 0
            else 0.0
        )
        account_number_accuracy = (
            ((total_extractions - total_account_corrections) / total_extractions * 100)
            if total_extractions > 0
            else 0.0
        )

        return {
            "total_extractions": total_extractions,
            "total_corrections": logs_with_any_correction,
            "accuracy_rate": round(accuracy_rate, 2),
            "this_week": this_week_count,
            "owner_accuracy": round(owner_accuracy, 2),
            "bank_name_accuracy": round(bank_name_accuracy, 2),
            "account_number_accuracy": round(account_number_accuracy, 2),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")
    finally:
        if session:
            session.close()
