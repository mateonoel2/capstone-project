import tempfile
from pathlib import Path

from fastapi import UploadFile

from application.modules.extraction.entities import ExtractionLog
from application.modules.extraction.repository import ExtractionRepository
from src.extraction.claude_ocr_parser import ClaudeOCRParser


class ExtractionResult:
    def __init__(self, owner: str, bank_name: str, account_number: str):
        self.owner = owner
        self.bank_name = bank_name
        self.account_number = account_number


class SubmissionData:
    def __init__(
        self,
        filename: str,
        extracted_owner: str,
        extracted_bank_name: str,
        extracted_account_number: str,
        final_owner: str,
        final_bank_name: str,
        final_account_number: str,
    ):
        self.filename = filename
        self.extracted_owner = extracted_owner
        self.extracted_bank_name = extracted_bank_name
        self.extracted_account_number = extracted_account_number
        self.final_owner = final_owner
        self.final_bank_name = final_bank_name
        self.final_account_number = final_account_number


class MetricsData:
    def __init__(
        self,
        total_extractions: int,
        total_corrections: int,
        accuracy_rate: float,
        this_week: int,
        owner_accuracy: float,
        bank_name_accuracy: float,
        account_number_accuracy: float,
    ):
        self.total_extractions = total_extractions
        self.total_corrections = total_corrections
        self.accuracy_rate = accuracy_rate
        self.this_week = this_week
        self.owner_accuracy = owner_accuracy
        self.bank_name_accuracy = bank_name_accuracy
        self.account_number_accuracy = account_number_accuracy


class ExtractionService:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

    async def extract_from_pdf(self, file: UploadFile) -> ExtractionResult:
        if not file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported")

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = Path(tmp_file.name)

            parser = ClaudeOCRParser()
            result = parser.parse_file(tmp_file_path)

            tmp_file_path.unlink()

            return ExtractionResult(
                owner="" if result.owner == "Unknown" else result.owner,
                bank_name="" if result.bank_name == "Unknown" else result.bank_name,
                account_number=""
                if result.account_number == "000000000000000000"
                else result.account_number,
            )

        except Exception as e:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()
            raise e

    def submit_extraction(self, submission: SubmissionData) -> int:
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

        created_log = self.repository.create(log_entry)
        return created_log.id

    def get_extraction_logs(
        self, page: int, page_size: int
    ) -> tuple[list[ExtractionLog], int, int]:
        if page < 1:
            raise ValueError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        logs, total = self.repository.get_all_paginated(page, page_size)
        total_pages = (total + page_size - 1) // page_size
        return logs, total, total_pages

    def get_metrics(self) -> MetricsData:
        total_extractions = self.repository.count_total()

        if total_extractions == 0:
            return MetricsData(
                total_extractions=0,
                total_corrections=0,
                accuracy_rate=0.0,
                this_week=0,
                owner_accuracy=0.0,
                bank_name_accuracy=0.0,
                account_number_accuracy=0.0,
            )

        total_owner_corrections = self.repository.count_with_field_correction("owner")
        total_bank_corrections = self.repository.count_with_field_correction("bank_name")
        total_account_corrections = self.repository.count_with_field_correction("account_number")
        logs_with_any_correction = self.repository.count_with_any_correction()
        this_week_count = self.repository.count_this_week()

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

        return MetricsData(
            total_extractions=total_extractions,
            total_corrections=logs_with_any_correction,
            accuracy_rate=round(accuracy_rate, 2),
            this_week=this_week_count,
            owner_accuracy=round(owner_accuracy, 2),
            bank_name_accuracy=round(bank_name_accuracy, 2),
            account_number_accuracy=round(account_number_accuracy, 2),
        )

