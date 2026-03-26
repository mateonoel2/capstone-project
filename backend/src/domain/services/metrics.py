import uuid

from src.domain.entities import MetricsData
from src.infrastructure.repository import ExtractionRepository


class MetricsService:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

    def get_metrics(
        self, extractor_config_id: uuid.UUID | None = None, user_id: uuid.UUID | None = None
    ) -> MetricsData:
        any_corrected, field_corrections, total = self.repository.count_corrections(
            extractor_config_id, user_id=user_id
        )
        this_week_count = self.repository.count_this_week(extractor_config_id, user_id=user_id)

        if total == 0:
            return MetricsData(
                total_extractions=0,
                total_corrections=0,
                accuracy_rate=0.0,
                this_week=0,
                field_accuracies={},
            )

        total_field_corrections = sum(field_corrections.values())
        num_fields = len(field_corrections) if field_corrections else 1
        total_fields = total * num_fields
        accuracy_rate = (
            ((total_fields - total_field_corrections) / total_fields * 100)
            if total_fields > 0
            else 0.0
        )

        field_accuracies = {}
        for field_name, correction_count in field_corrections.items():
            field_accuracies[field_name] = round((total - correction_count) / total * 100, 2)

        return MetricsData(
            total_extractions=total,
            total_corrections=any_corrected,
            accuracy_rate=round(accuracy_rate, 2),
            this_week=this_week_count,
            field_accuracies=field_accuracies,
        )
