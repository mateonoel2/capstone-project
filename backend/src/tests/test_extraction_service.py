import pytest

from src.domain.services.extraction import (
    _inject_valid_document_field,
    apply_bank_statement_postprocessing,
)


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


class TestInjectValidDocumentField:
    def test_adds_is_valid_document_when_missing(self):
        schema = {
            "type": "object",
            "properties": {
                "comercio": {"type": "string"},
            },
        }
        result = _inject_valid_document_field(schema)
        assert "is_valid_document" in result["properties"]
        assert result["properties"]["comercio"] == {"type": "string"}

    def test_does_not_overwrite_existing(self):
        schema = {
            "type": "object",
            "properties": {
                "is_valid_document": {"type": "boolean", "description": "custom"},
            },
        }
        result = _inject_valid_document_field(schema)
        assert result["properties"]["is_valid_document"]["description"] == "custom"

    def test_does_not_mutate_original(self):
        schema = {
            "type": "object",
            "properties": {"a": {"type": "string"}},
        }
        result = _inject_valid_document_field(schema)
        assert "is_valid_document" not in schema["properties"]
        assert "is_valid_document" in result["properties"]
