import pytest
from pydantic import ValidationError

from src.infrastructure.api.extraction.dtos import (
    ExtractorConfigCreateRequest,
    ExtractorConfigUpdateRequest,
)
from src.infrastructure.models import ExtractionLog


class TestCorrectedFieldsProperty:
    def _make_log(self, extracted: dict, final: dict) -> ExtractionLog:
        log = ExtractionLog()
        object.__setattr__(log, "extracted_fields", extracted)
        object.__setattr__(log, "final_fields", final)
        return log

    def test_matching_fields_not_corrected(self):
        log = self._make_log({"owner": "Juan"}, {"owner": "Juan"})
        assert log.corrected_fields == {"owner": False}

    def test_differing_fields_corrected(self):
        log = self._make_log({"owner": "Juan"}, {"owner": "María"})
        assert log.corrected_fields == {"owner": True}

    def test_empty_fields(self):
        log = self._make_log({}, {})
        assert log.corrected_fields == {}

    def test_mixed_corrections(self):
        log = self._make_log(
            {"owner": "Juan", "bank_name": "BBVA"},
            {"owner": "Juan", "bank_name": "BANAMEX"},
        )
        result = log.corrected_fields
        assert result["owner"] is False
        assert result["bank_name"] is True


class TestOutputSchemaValidator:
    def test_valid_schema_passes(self):
        req = ExtractorConfigCreateRequest(
            name="Test",
            prompt="Extract data",
            output_schema={
                "type": "object",
                "properties": {"field1": {"type": "string"}},
                "required": ["field1"],
            },
        )
        assert req.output_schema["properties"]["field1"]["type"] == "string"

    def test_missing_properties_raises(self):
        with pytest.raises(ValidationError, match="properties"):
            ExtractorConfigCreateRequest(
                name="Test",
                prompt="Extract data",
                output_schema={"type": "object", "required": []},
            )

    def test_missing_required_raises(self):
        with pytest.raises(ValidationError, match="required"):
            ExtractorConfigCreateRequest(
                name="Test",
                prompt="Extract data",
                output_schema={"type": "object", "properties": {}},
            )

    def test_update_none_schema_passes(self):
        req = ExtractorConfigUpdateRequest(output_schema=None)
        assert req.output_schema is None

    def test_update_invalid_schema_raises(self):
        with pytest.raises(ValidationError):
            ExtractorConfigUpdateRequest(output_schema={"type": "object"})
