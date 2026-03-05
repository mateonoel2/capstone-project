from src.domain.entities import ApiCallMetricsData
from src.infrastructure.repository import ApiCallRepository


class ApiMetricsService:
    def __init__(self, repository: ApiCallRepository):
        self.repository = repository

    def get_metrics(self) -> ApiCallMetricsData:
        total = self.repository.count_total()
        failures = self.repository.count_failures()
        error_rate = round((failures / total) * 100, 1) if total > 0 else 0.0

        error_breakdown = [
            {"error_type": error_type, "count": count}
            for error_type, count in self.repository.count_by_error_type()
        ]

        return ApiCallMetricsData(
            total_calls=total,
            total_failures=failures,
            error_rate=error_rate,
            avg_response_time_ms=self.repository.avg_response_time_ms(),
            calls_this_week=self.repository.count_this_week(),
            error_breakdown=error_breakdown,
        )
