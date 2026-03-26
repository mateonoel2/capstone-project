import uuid

from src.domain.entities import SubmissionData
from src.infrastructure.models import ExtractionLog
from src.infrastructure.repository import ExtractionRepository


class SubmissionService:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

    def submit_extraction(
        self,
        submission: SubmissionData,
        extractor_config_id: uuid.UUID | None = None,
        extractor_config_version_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        log_entry = ExtractionLog(
            filename=submission.filename,
            extracted_fields=submission.extracted_fields,
            final_fields=submission.final_fields,
            extractor_config_id=extractor_config_id,
            extractor_config_version_id=extractor_config_version_id,
            user_id=user_id,
        )

        created_log = self.repository.create(log_entry)
        return created_log.id  # type: ignore[return-value]

    def get_extraction_logs(
        self,
        page: int,
        page_size: int,
        extractor_config_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ) -> tuple[list[ExtractionLog], int, int]:
        if page < 1:
            raise ValueError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        logs, total = self.repository.get_all_paginated(
            page, page_size, extractor_config_id, user_id=user_id
        )
        total_pages = (total + page_size - 1) // page_size
        return logs, total, total_pages
