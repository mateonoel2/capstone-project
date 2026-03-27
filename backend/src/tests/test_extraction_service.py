import pytest

from src.domain.services.extraction import apply_bank_statement_postprocessing


class TestApplyBankStatementPostprocessing:
    def test_valid_bank_statement(self):
        raw = {
            "owner": "Juan Pérez",
            "account_number": "012345678901234567",
            "bank_name": "BBVA",
        }
        result = apply_bank_statement_postprocessing(raw)
        assert result["owner"] == "Juan Pérez"
        assert result["account_number"] == "012345678901234567"

    def test_unknown_bank_and_account_raises(self):
        with pytest.raises(ValueError, match="No se encontró información bancaria"):
            apply_bank_statement_postprocessing(
                {
                    "owner": "Juan",
                    "account_number": "000000000000000000",
                    "bank_name": "Unknown",
                }
            )

    def test_clabe_with_spaces_stripped(self):
        raw = {
            "owner": "Ana",
            "account_number": "072 691 00844421773 3",
            "bank_name": "BANORTE",
        }
        result = apply_bank_statement_postprocessing(raw)
        # Spaces stripped, first 18 digits taken
        assert " " not in result["account_number"]
        assert len(result["account_number"]) <= 18

    def test_clabe_truncated_to_18_digits(self):
        raw = {
            "owner": "Ana",
            "account_number": "0123456789012345678",  # 19 digits
            "bank_name": "BBVA",
        }
        result = apply_bank_statement_postprocessing(raw)
        assert len(result["account_number"]) == 18
