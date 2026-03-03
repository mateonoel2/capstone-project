from src.domain.entities import SubmissionData
from src.infrastructure.models import ExtractionLog
from src.infrastructure.repository import ExtractionRepository


class SubmissionService:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

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
        return int(created_log.id)  # type: ignore[arg-type]

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
