from src.domain.entities import ApiCallMetricsData
from src.infrastructure.repository import ApiCallRepository


class ApiMetricsService:
    def __init__(self, repository: ApiCallRepository):
        self.repository = repository

    def get_metrics(
        self, extractor_config_id: int | None = None, user_id: int | None = None
    ) -> ApiCallMetricsData:
        total = self.repository.count_total(extractor_config_id, user_id=user_id)
        failures = self.repository.count_failures(extractor_config_id, user_id=user_id)
        error_rate = round((failures / total) * 100, 1) if total > 0 else 0.0

        error_breakdown = [
            {"error_type": error_type, "count": count}
            for error_type, count in self.repository.count_by_error_type(
                extractor_config_id, user_id=user_id
            )
        ]

        return ApiCallMetricsData(
            total_calls=total,
            total_failures=failures,
            error_rate=error_rate,
            avg_response_time_ms=self.repository.avg_response_time_ms(
                extractor_config_id, user_id=user_id
            ),
            calls_this_week=self.repository.count_this_week(extractor_config_id, user_id=user_id),
            error_breakdown=error_breakdown,
        )
