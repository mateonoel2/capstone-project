from dataclasses import dataclass


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
