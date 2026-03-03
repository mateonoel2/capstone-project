from src.domain.entities import MetricsData
from src.infrastructure.repository import ExtractionRepository


class MetricsService:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

    def get_metrics(self) -> MetricsData:
        total_extractions = self.repository.count_total()

        if total_extractions == 0:
            return MetricsData(
                total_extractions=0,
                total_corrections=0,
                accuracy_rate=0.0,
                this_week=0,
                owner_accuracy=0.0,
                bank_name_accuracy=0.0,
                account_number_accuracy=0.0,
            )

        total_owner_corrections = self.repository.count_with_field_correction("owner")
        total_bank_corrections = self.repository.count_with_field_correction("bank_name")
        total_account_corrections = self.repository.count_with_field_correction("account_number")
        logs_with_any_correction = self.repository.count_with_any_correction()
        this_week_count = self.repository.count_this_week()

        total_fields = total_extractions * 3
        total_field_corrections = (
            total_owner_corrections + total_bank_corrections + total_account_corrections
        )
        accuracy_rate = (
            ((total_fields - total_field_corrections) / total_fields * 100)
            if total_fields > 0
            else 0.0
        )

        owner_accuracy = (
            ((total_extractions - total_owner_corrections) / total_extractions * 100)
            if total_extractions > 0
            else 0.0
        )
        bank_name_accuracy = (
            ((total_extractions - total_bank_corrections) / total_extractions * 100)
            if total_extractions > 0
            else 0.0
        )
        account_number_accuracy = (
            ((total_extractions - total_account_corrections) / total_extractions * 100)
            if total_extractions > 0
            else 0.0
        )

        return MetricsData(
            total_extractions=total_extractions,
            total_corrections=logs_with_any_correction,
            accuracy_rate=round(accuracy_rate, 2),
            this_week=this_week_count,
            owner_accuracy=round(owner_accuracy, 2),
            bank_name_accuracy=round(bank_name_accuracy, 2),
            account_number_accuracy=round(account_number_accuracy, 2),
        )
