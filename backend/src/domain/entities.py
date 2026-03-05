from dataclasses import dataclass, field


@dataclass
class ApiCallResult:
    model: str
    success: bool
    response_time_ms: float
    error_type: str | None = None
    error_message: str | None = None


@dataclass
class ApiCallMetricsData:
    total_calls: int
    total_failures: int
    error_rate: float
    avg_response_time_ms: float
    calls_this_week: int
    error_breakdown: list[dict[str, object]] = field(default_factory=list)


class ExtractionError(Exception):
    def __init__(self, message: str, call_result: ApiCallResult):
        super().__init__(message)
        self.call_result = call_result


@dataclass
class SubmissionData:
    filename: str
    extracted_owner: str
    extracted_bank_name: str
    extracted_account_number: str
    final_owner: str
    final_bank_name: str
    final_account_number: str


@dataclass
class MetricsData:
    total_extractions: int
    total_corrections: int
    accuracy_rate: float
    this_week: int
    owner_accuracy: float
    bank_name_accuracy: float
    account_number_accuracy: float
