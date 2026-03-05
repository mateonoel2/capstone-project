from src.domain.entities import SubmissionData
from src.infrastructure.models import ExtractionLog
from src.infrastructure.repository import ExtractionRepository


class SubmissionService:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

    def submit_extraction(
        self, submission: SubmissionData, parser_config_id: int | None = None
    ) -> int:
        log_entry = ExtractionLog(
            filename=submission.filename,
            extracted_fields=submission.extracted_fields,
            final_fields=submission.final_fields,
            parser_config_id=parser_config_id,
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
