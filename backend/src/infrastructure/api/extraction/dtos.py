from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ExtractionResponse(BaseModel):
    owner: str
    bank_name: str
    account_number: str


class SubmissionRequest(BaseModel):
    filename: str
    extracted_owner: str
    extracted_bank_name: str
    extracted_account_number: str
    final_owner: str
    final_bank_name: str
    final_account_number: str


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
    extracted_owner: str
    extracted_bank_name: str
    extracted_account_number: str
    final_owner: str
    final_bank_name: str
    final_account_number: str
    owner_corrected: bool
    bank_name_corrected: bool
    account_number_corrected: bool

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
    owner_accuracy: float
    bank_name_accuracy: float
    account_number_accuracy: float
