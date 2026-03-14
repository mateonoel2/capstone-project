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
    extracted_fields: dict[str, str]
    final_fields: dict[str, str]


@dataclass
class ExtractorConfigData:
    id: int | None
    name: str
    description: str
    prompt: str
    model: str
    output_schema: dict
    is_default: bool
    status: str = "active"
    created_at: object | None = None
    updated_at: object | None = None


@dataclass
class ExtractorConfigVersionData:
    id: int
    extractor_config_id: int
    version_number: int
    prompt: str
    model: str
    output_schema: dict
    is_active: bool
    created_at: object | None = None


@dataclass
class MetricsData:
    total_extractions: int
    total_corrections: int
    accuracy_rate: float
    this_week: int
    field_accuracies: dict[str, float] = field(default_factory=dict)
