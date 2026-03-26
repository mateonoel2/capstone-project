import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ExtractionResponse(BaseModel):
    fields: dict[str, Any] = {}
    extractor_config_id: uuid.UUID | None = None
    extractor_config_name: str = ""
    extractor_config_version_id: uuid.UUID | None = None
    extractor_config_version_number: int | None = None


class SubmissionRequest(BaseModel):
    filename: str
    extracted_fields: dict[str, str]
    final_fields: dict[str, str]
    extractor_config_id: uuid.UUID | None = None
    extractor_config_version_id: uuid.UUID | None = None


class SubmissionResponse(BaseModel):
    message: str
    id: uuid.UUID


class Bank(BaseModel):
    name: str
    code: str


class BanksResponse(BaseModel):
    banks: list[Bank]


class ExtractionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: str | None
    filename: str
    extracted_fields: dict[str, Any] = {}
    final_fields: dict[str, Any] = {}
    corrected_fields: dict[str, bool] = {}
    extractor_config_version_id: uuid.UUID | None = None
    extractor_config_name: str | None = None

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


def _validate_output_schema(v: dict[str, Any]) -> dict[str, Any]:
    if "properties" not in v or not isinstance(v["properties"], dict):
        raise ValueError("output_schema debe tener 'properties' como objeto")
    if "required" not in v or not isinstance(v["required"], list):
        raise ValueError("output_schema debe tener 'required' como lista")
    return v


class ExtractorConfigCreateRequest(BaseModel):
    name: str
    description: str = ""
    prompt: str = ""
    model: str = "claude-haiku-4-5-20251001"
    output_schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    is_default: bool = False
    status: str = "active"

    @field_validator("output_schema")
    @classmethod
    def validate_schema(cls, v: dict[str, Any], info: Any) -> dict[str, Any]:
        status = info.data.get("status", "active")
        if status == "draft":
            return v
        return _validate_output_schema(v)

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str, info: Any) -> str:
        status = info.data.get("status", "active")
        if status != "draft" and not v.strip():
            raise ValueError("El prompt es requerido para extractores activos")
        return v


class ExtractorConfigUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt: str | None = None
    model: str | None = None
    output_schema: dict[str, Any] | None = None
    is_default: bool | None = None
    status: str | None = None

    @field_validator("output_schema")
    @classmethod
    def validate_schema(cls, v: dict[str, Any] | None, info: Any) -> dict[str, Any] | None:
        if v is not None:
            status = info.data.get("status")
            if status == "draft":
                return v
            return _validate_output_schema(v)
        return v


class ExtractorConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    prompt: str
    model: str
    output_schema: dict[str, Any]
    is_default: bool
    status: str = "active"
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

    id: uuid.UUID
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
    is_available: bool = True


class GenerateSchemaRequest(BaseModel):
    description: str


class GenerateSchemaResponse(BaseModel):
    output_schema: dict[str, Any]


class GeneratePromptRequest(BaseModel):
    output_schema: dict[str, Any]
    document_type: str | None = None


class GeneratePromptResponse(BaseModel):
    prompt: str


class UpdatePromptRequest(BaseModel):
    current_prompt: str
    instructions: str
    output_schema: dict[str, Any]


class TestExtractResponse(BaseModel):
    fields: dict[str, Any]
    response_time_ms: float
    test_log_id: uuid.UUID | None = None


class SetActiveRequest(BaseModel):
    is_active: bool


class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str


class UploadUrlResponse(BaseModel):
    s3_key: str
    upload_url: str | None
    filename: str


class ExtractRequest(BaseModel):
    s3_key: str
    filename: str
    extractor_config_id: uuid.UUID | None = None


class TestExtractionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: str | None
    filename: str
    s3_key: str
    extractor_config_id: uuid.UUID | None
    prompt_snapshot: str
    model: str
    output_schema_snapshot: dict[str, Any]
    extracted_fields: dict[str, Any] | None
    success: bool
    error_message: str | None
    response_time_ms: float

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_timestamp(cls, v: datetime | str | None) -> str | None:
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class TestExtractRequest(BaseModel):
    s3_key: str
    filename: str
    config: dict[str, Any]
    extractor_config_id: uuid.UUID | None = None
