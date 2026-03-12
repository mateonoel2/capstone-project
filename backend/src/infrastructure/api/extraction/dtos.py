from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ExtractionResponse(BaseModel):
    fields: dict[str, Any] = {}
    extractor_config_id: int | None = None
    extractor_config_name: str = ""
    extractor_config_version_id: int | None = None
    extractor_config_version_number: int | None = None


class SubmissionRequest(BaseModel):
    filename: str
    extracted_fields: dict[str, str]
    final_fields: dict[str, str]
    extractor_config_id: int | None = None
    extractor_config_version_id: int | None = None


class SubmissionResponse(BaseModel):
    message: str
    id: int


class Bank(BaseModel):
    name: str
    code: str


class BanksResponse(BaseModel):
    banks: list[Bank]


class ExtractionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: str | None
    filename: str
    extracted_fields: dict[str, Any] = {}
    final_fields: dict[str, Any] = {}
    corrected_fields: dict[str, bool] = {}
    extractor_config_version_id: int | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_timestamp(cls, v: datetime | str | None) -> str | None:
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class LogsResponse(BaseModel):
    logs: list[ExtractionLogResponse]
    pagination: PaginationMeta


class MetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_extractions: int
    total_corrections: int
    accuracy_rate: float
    this_week: int
    field_accuracies: dict[str, float] = {}


class ErrorBreakdownItem(BaseModel):
    error_type: str
    count: int


class ApiCallMetricsResponse(BaseModel):
    total_calls: int
    total_failures: int
    error_rate: float
    avg_response_time_ms: float
    calls_this_week: int
    error_breakdown: list[ErrorBreakdownItem]


class ExtractorConfigCreateRequest(BaseModel):
    name: str
    description: str = ""
    prompt: str
    model: str = "claude-haiku-4-5-20251001"
    output_schema: dict[str, Any]
    is_default: bool = False


class ExtractorConfigUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt: str | None = None
    model: str | None = None
    output_schema: dict[str, Any] | None = None
    is_default: bool | None = None


class ExtractorConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    prompt: str
    model: str
    output_schema: dict[str, Any]
    is_default: bool
    created_at: str | None
    updated_at: str | None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_timestamps(cls, v: datetime | str | None) -> str | None:
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class ExtractorConfigListResponse(BaseModel):
    configs: list[ExtractorConfigResponse]


class ExtractorConfigVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    prompt: str
    model: str
    output_schema: dict[str, Any]
    is_active: bool = False
    created_at: str | None

    @field_validator("created_at", mode="before")
    @classmethod
    def convert_timestamp(cls, v: datetime | str | None) -> str | None:
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class ModelInfo(BaseModel):
    id: str
    name: str
    tier: str
    cost_hint: str


class GenerateSchemaRequest(BaseModel):
    description: str


class GenerateSchemaResponse(BaseModel):
    output_schema: dict[str, Any]


class GeneratePromptRequest(BaseModel):
    output_schema: dict[str, Any]
    document_type: str | None = None


class GeneratePromptResponse(BaseModel):
    prompt: str


class TestExtractResponse(BaseModel):
    fields: dict[str, Any]
    response_time_ms: float


class SetActiveRequest(BaseModel):
    is_active: bool
