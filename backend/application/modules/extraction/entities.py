class ExtractionResult:
    def __init__(self, owner: str, bank_name: str, account_number: str):
        self.owner = owner
        self.bank_name = bank_name
        self.account_number = account_number


class SubmissionData:
    def __init__(
        self,
        filename: str,
        extracted_owner: str,
        extracted_bank_name: str,
        extracted_account_number: str,
        final_owner: str,
        final_bank_name: str,
        final_account_number: str,
    ):
        self.filename = filename
        self.extracted_owner = extracted_owner
        self.extracted_bank_name = extracted_bank_name
        self.extracted_account_number = extracted_account_number
        self.final_owner = final_owner
        self.final_bank_name = final_bank_name
        self.final_account_number = final_account_number


class MetricsData:
    def __init__(
        self,
        total_extractions: int,
        total_corrections: int,
        accuracy_rate: float,
        this_week: int,
        owner_accuracy: float,
        bank_name_accuracy: float,
        account_number_accuracy: float,
    ):
        self.total_extractions = total_extractions
        self.total_corrections = total_corrections
        self.accuracy_rate = accuracy_rate
        self.this_week = this_week
        self.owner_accuracy = owner_accuracy
        self.bank_name_accuracy = bank_name_accuracy
        self.account_number_accuracy = account_number_accuracy

