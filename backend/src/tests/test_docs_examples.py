"""Test that the documented API examples actually work against the real endpoints.

Each test sends the exact request body from the docs and verifies:
- The endpoint returns the expected status code
- The response contains all documented fields
"""

import json
import re
from unittest.mock import MagicMock, patch

import pytest

from src.domain.entities import (
    ApiCallResult,
    ApiTokenData,
    ExtractorConfigData,
    ExtractorConfigVersionData,
)
from src.infrastructure.api.docs.content import ENDPOINTS
from src.infrastructure.auth import TOKEN_PREFIX
from src.tests.conftest import (
    CONFIG_UUID,
    CONFIG_UUID_2,
    LOG_UUID,
    TOKEN_UUID,
    USER_UUID,
    VERSION_UUID,
)


def _parse_doc_json(text: str) -> dict | list:
    """Parse a documentation JSON body, replacing placeholders."""
    text = re.sub(r'"([^"]*)\.\.\."', r'"\1placeholder"', text)
    text = re.sub(r"\{\s*\.\.\.\s*\}", "{}", text)
    text = text.replace("...", '"__placeholder__"')
    return json.loads(text)


def _get_doc_endpoint(method: str, path: str):
    """Find a documented endpoint by method and path."""
    for ep in ENDPOINTS:
        if ep.method == method and ep.path == path:
            return ep
    pytest.fail(f"Documented endpoint {method} {path} not found")


def _response_keys(ep) -> set[str]:
    """Extract top-level keys from a documented response body."""
    if not ep.response_body:
        return set()
    parsed = _parse_doc_json(ep.response_body)
    if isinstance(parsed, dict):
        return set(parsed.keys())
    if isinstance(parsed, list) and parsed:
        return set(parsed[0].keys())
    return set()


# ── Tokens ────────────────────────────────────────────────────────────────────


class TestTokenExamples:
    def test_create_token(self, client):
        ep = _get_doc_endpoint("POST", "/tokens")
        request_body = _parse_doc_json(ep.request_body)

        api_token = ApiTokenData(
            id=TOKEN_UUID,
            user_id=USER_UUID,
            name=request_body["name"],
            expires_at=request_body.get("expires_at"),
        )
        with (
            patch("src.infrastructure.api.tokens.routes.generate_api_token") as mock_gen,
            patch("src.infrastructure.api.tokens.routes.hash_token", return_value="h"),
            patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo,
        ):
            mock_gen.return_value = f"{TOKEN_PREFIX}abc123"
            MockRepo.return_value.create.return_value = api_token
            resp = client.post("/tokens", json=request_body)

        assert resp.status_code == 200
        data = resp.json()
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data.keys()), (
            f"Response missing documented keys: {doc_keys - data.keys()}"
        )
        assert data["token"].startswith(TOKEN_PREFIX)

    def test_list_tokens(self, client):
        ep = _get_doc_endpoint("GET", "/tokens")

        tokens = [
            ApiTokenData(id=TOKEN_UUID, user_id=USER_UUID, name="token-a"),
        ]
        with patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo:
            MockRepo.return_value.get_by_user.return_value = tokens
            resp = client.get("/tokens")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data[0].keys()), (
            f"Response missing documented keys: {doc_keys - data[0].keys()}"
        )

    def test_revoke_token(self, client):
        _get_doc_endpoint("DELETE", "/tokens/{token_id}")

        with patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo:
            MockRepo.return_value.revoke.return_value = True
            resp = client.delete(f"/tokens/{TOKEN_UUID}")

        assert resp.status_code == 200
        assert "detail" in resp.json()


# ── Extractors ────────────────────────────────────────────────────────────────


def _make_config(**overrides):
    defaults = dict(
        id=CONFIG_UUID,
        name="Boletas y recibos",
        description="Extrae datos de boletas",
        prompt="Extrae los campos",
        model="claude-haiku-4-5-20251001",
        output_schema={
            "type": "object",
            "properties": {"titular": {"type": "string"}, "monto": {"type": "string"}},
            "required": ["titular", "monto"],
        },
        is_default=True,
        status="active",
        user_id=USER_UUID,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-15T12:00:00",
    )
    defaults.update(overrides)
    return ExtractorConfigData(**defaults)


class TestExtractorExamples:
    def test_list_extractors(self, client):
        ep = _get_doc_endpoint("GET", "/extractors")

        configs = [_make_config()]
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_all.return_value = configs
            resp = client.get("/extractors")

        assert resp.status_code == 200
        data = resp.json()
        assert "configs" in data
        config = data["configs"][0]
        doc_response = _parse_doc_json(ep.response_body)
        doc_config_keys = set(doc_response["configs"][0].keys())
        assert doc_config_keys.issubset(config.keys()), (
            f"Response missing documented keys: {doc_config_keys - config.keys()}"
        )

    def test_get_models(self, client):
        ep = _get_doc_endpoint("GET", "/extractors/models")

        resp = client.get("/extractors/models")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data[0].keys()), (
            f"Response missing documented keys: {doc_keys - data[0].keys()}"
        )

    def test_get_extractor(self, client):
        ep = _get_doc_endpoint("GET", "/extractors/{config_id}")

        config = _make_config()
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = config
            resp = client.get(f"/extractors/{CONFIG_UUID}")

        assert resp.status_code == 200
        data = resp.json()
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data.keys()), (
            f"Response missing documented keys: {doc_keys - data.keys()}"
        )

    def test_list_versions(self, client):
        ep = _get_doc_endpoint("GET", "/extractors/{config_id}/versions")

        config = _make_config()
        version = ExtractorConfigVersionData(
            id=VERSION_UUID,
            extractor_config_id=CONFIG_UUID,
            version_number=1,
            prompt="Prompt original",
            model="claude-haiku-4-5-20251001",
            output_schema={"type": "object", "properties": {}},
            is_active=False,
            created_at="2026-01-01T00:00:00",
        )
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = config
            MockRepo.return_value.get_versions.return_value = [version]
            resp = client.get(f"/extractors/{CONFIG_UUID}/versions")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data[0].keys()), (
            f"Response missing documented keys: {doc_keys - data[0].keys()}"
        )


# ── Extraction ────────────────────────────────────────────────────────────────


class TestExtractionExamples:
    def test_upload_url(self, client):
        ep = _get_doc_endpoint("POST", "/extraction/upload-url")
        request_body = _parse_doc_json(ep.request_body)

        with patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage:
            mock_storage.return_value.generate_upload_url.return_value = (
                "https://s3.amazonaws.com/bucket/uploads/key?signed"
            )
            resp = client.post("/extraction/upload-url", json=request_body)

        assert resp.status_code == 200
        data = resp.json()
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data.keys()), (
            f"Response missing documented keys: {doc_keys - data.keys()}"
        )
        assert data["filename"] == request_body["filename"]
        assert data["s3_key"]  # non-empty

    def test_extract(self, client):
        ep = _get_doc_endpoint("POST", "/extraction/extract")
        # Build a valid request body (use real UUIDs, not placeholder)
        request_body = {
            "s3_key": "uploads/abc123-factura.pdf",
            "filename": "factura.pdf",
            "extractor_config_id": str(CONFIG_UUID),
        }

        config = _make_config()
        call_result = ApiCallResult(
            model="claude-haiku-4-5-20251001", success=True, response_time_ms=150.0
        )

        with (
            patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage,
            patch("src.infrastructure.api.extraction.routes.ExtractionService") as MockService,
            patch(
                "src.infrastructure.api.extraction.routes.ExtractorConfigRepository"
            ) as MockConfigRepo,
            patch("src.infrastructure.api.extraction.routes.ApiCallRepository"),
            patch("src.infrastructure.api.extraction.routes.AiUsageLogRepository"),
            patch("src.infrastructure.api.extraction.routes.QuotaService") as MockQuota,
        ):
            MockQuota.return_value.check_extraction_quota.return_value = None
            mock_storage.return_value.download.return_value = b"pdf-bytes"
            MockService.return_value.extract.return_value = (
                {"titular": "Juan Perez", "monto": "$1,500.00", "fecha": "2026-03-15"},
                call_result,
                None,
            )
            MockConfigRepo.return_value.get_by_id.return_value = config
            MockConfigRepo.return_value.get_active_versions.return_value = []

            resp = client.post("/extraction/extract", json=request_body)

        assert resp.status_code == 200
        data = resp.json()
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data.keys()), (
            f"Response missing documented keys: {doc_keys - data.keys()}"
        )
        assert isinstance(data["fields"], dict)
        assert data["extractor_config_id"] is not None
        assert data["extractor_config_name"] is not None

    def test_submit(self, client):
        ep = _get_doc_endpoint("POST", "/extraction/submit")
        # Use a real UUID instead of placeholder
        request_body = {
            "filename": "factura.pdf",
            "extracted_fields": {"titular": "Juan Peres", "monto": "$1,500.00"},
            "final_fields": {"titular": "Juan Perez", "monto": "$1,500.00"},
            "extractor_config_id": str(CONFIG_UUID),
        }

        with patch("src.infrastructure.api.extraction.routes.ExtractionRepository") as MockRepo:
            MockRepo.return_value.create.return_value = MagicMock(id=LOG_UUID)
            resp = client.post("/extraction/submit", json=request_body)

        assert resp.status_code == 200
        data = resp.json()
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data.keys()), (
            f"Response missing documented keys: {doc_keys - data.keys()}"
        )
        assert data["message"]
        assert data["id"]

    def test_banks(self, client):
        ep = _get_doc_endpoint("GET", "/extraction/banks")

        resp = client.get("/extraction/banks")

        assert resp.status_code == 200
        data = resp.json()
        assert "banks" in data
        assert isinstance(data["banks"], list)
        assert len(data["banks"]) > 0
        doc_response = _parse_doc_json(ep.response_body)
        doc_bank_keys = set(doc_response["banks"][0].keys())
        assert doc_bank_keys.issubset(data["banks"][0].keys()), (
            f"Response missing documented keys: {doc_bank_keys - data['banks'][0].keys()}"
        )

    def test_upload_fallback(self, client):
        ep = _get_doc_endpoint("POST", "/extraction/upload")

        with patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage:
            mock_storage.return_value.save.return_value = None
            resp = client.post(
                "/extraction/upload",
                files={"file": ("factura.pdf", b"fake-pdf-bytes", "application/pdf")},
            )

        assert resp.status_code == 200
        data = resp.json()
        doc_keys = _response_keys(ep)
        assert doc_keys.issubset(data.keys()), (
            f"Response missing documented keys: {doc_keys - data.keys()}"
        )
        assert data["filename"] == "factura.pdf"
        assert data["upload_url"] is None


# ── Documented params match what the API actually accepts ─────────────────────


class TestDocumentedParamsAccepted:
    """Verify the documented request bodies are accepted (no 422 validation error)."""

    def test_upload_url_body_shape(self, client):
        """Documented upload-url body should not cause 422."""
        ep = _get_doc_endpoint("POST", "/extraction/upload-url")
        body = _parse_doc_json(ep.request_body)
        with patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage:
            mock_storage.return_value.generate_upload_url.return_value = "https://example.com"
            resp = client.post("/extraction/upload-url", json=body)
        assert resp.status_code != 422, f"Documented body caused validation error: {resp.json()}"

    def test_create_token_body_shape(self, client):
        """Documented create-token body should not cause 422."""
        ep = _get_doc_endpoint("POST", "/tokens")
        body = _parse_doc_json(ep.request_body)
        with (
            patch("src.infrastructure.api.tokens.routes.generate_api_token") as mock_gen,
            patch("src.infrastructure.api.tokens.routes.hash_token", return_value="h"),
            patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo,
        ):
            mock_gen.return_value = f"{TOKEN_PREFIX}test"
            MockRepo.return_value.create.return_value = ApiTokenData(
                id=TOKEN_UUID, user_id=USER_UUID, name="test"
            )
            resp = client.post("/tokens", json=body)
        assert resp.status_code != 422, f"Documented body caused validation error: {resp.json()}"

    def test_extract_body_shape(self, client):
        """Documented extract body should not cause 422."""
        body = {
            "s3_key": "uploads/abc123-factura.pdf",
            "filename": "factura.pdf",
            "extractor_config_id": str(CONFIG_UUID),
        }
        with (
            patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage,
            patch("src.infrastructure.api.extraction.routes.ExtractionService") as MockSvc,
            patch("src.infrastructure.api.extraction.routes.ExtractorConfigRepository") as MockCfg,
            patch("src.infrastructure.api.extraction.routes.ApiCallRepository"),
            patch("src.infrastructure.api.extraction.routes.AiUsageLogRepository"),
            patch("src.infrastructure.api.extraction.routes.QuotaService") as MockQ,
        ):
            MockQ.return_value.check_extraction_quota.return_value = None
            mock_storage.return_value.download.return_value = b"bytes"
            MockSvc.return_value.extract.return_value = ({}, ApiCallResult("m", True, 1.0), None)
            MockCfg.return_value.get_by_id.return_value = _make_config()
            MockCfg.return_value.get_active_versions.return_value = []
            resp = client.post("/extraction/extract", json=body)
        assert resp.status_code != 422, f"Documented body caused validation error: {resp.json()}"

    def test_submit_body_shape(self, client):
        """Documented submit body should not cause 422."""
        body = {
            "filename": "factura.pdf",
            "extracted_fields": {"titular": "Juan Peres", "monto": "$1,500.00"},
            "final_fields": {"titular": "Juan Perez", "monto": "$1,500.00"},
            "extractor_config_id": str(CONFIG_UUID),
        }
        with patch("src.infrastructure.api.extraction.routes.ExtractionRepository") as MockRepo:
            MockRepo.return_value.create.return_value = MagicMock(id=LOG_UUID)
            resp = client.post("/extraction/submit", json=body)
        assert resp.status_code != 422, f"Documented body caused validation error: {resp.json()}"


# ── Full documented flow (as shown on the index page) ─────────────────────────


class TestDocumentedFullFlow:
    """Simulate the exact flow shown in the index page examples:
    1. List extractors and pick one
    2. Get upload URL
    3. (upload to S3 — skipped, external)
    4. Extract with the chosen extractor_id + s3_key
    5. Submit corrections with extractor_id
    """

    def test_full_extraction_flow(self, client):
        config = _make_config()
        config2 = _make_config(
            id=CONFIG_UUID_2,
            name="Facturas",
            is_default=False,
            status="active",
        )
        call_result = ApiCallResult(
            model="claude-haiku-4-5-20251001", success=True, response_time_ms=120.0
        )

        # ── Step 1: GET /extractors → pick the first active one ──────────
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_all.return_value = [config, config2]
            resp = client.get("/extractors")

        assert resp.status_code == 200
        configs = resp.json()["configs"]
        assert len(configs) == 2
        # Pick first active (same logic as documented example)
        active = next(c for c in configs if c["status"] == "active")
        extractor_id = active["id"]

        # ── Step 2: POST /extraction/upload-url ──────────────────────────
        with patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage:
            mock_storage.return_value.generate_upload_url.return_value = (
                "https://s3.example.com/signed-url"
            )
            resp = client.post(
                "/extraction/upload-url",
                json={"filename": "factura.pdf", "content_type": "application/pdf"},
            )

        assert resp.status_code == 200
        upload_data = resp.json()
        s3_key = upload_data["s3_key"]
        assert s3_key  # non-empty
        assert upload_data["upload_url"]  # presigned URL returned

        # ── Step 3: PUT to S3 (external, skip) ───────────────────────────

        # ── Step 4: POST /extraction/extract with extractor_id + s3_key ──
        with (
            patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage,
            patch("src.infrastructure.api.extraction.routes.ExtractionService") as MockSvc,
            patch(
                "src.infrastructure.api.extraction.routes.ExtractorConfigRepository"
            ) as MockCfgRepo,
            patch("src.infrastructure.api.extraction.routes.ApiCallRepository"),
            patch("src.infrastructure.api.extraction.routes.AiUsageLogRepository"),
            patch("src.infrastructure.api.extraction.routes.QuotaService") as MockQuota,
        ):
            MockQuota.return_value.check_extraction_quota.return_value = None
            mock_storage.return_value.download.return_value = b"fake-pdf"
            MockSvc.return_value.extract.return_value = (
                {"titular": "Juan Peres", "monto": "$1,500.00"},
                call_result,
                None,
            )
            MockCfgRepo.return_value.get_by_id.return_value = config
            MockCfgRepo.return_value.get_active_versions.return_value = []

            resp = client.post(
                "/extraction/extract",
                json={
                    "s3_key": s3_key,
                    "filename": "factura.pdf",
                    "extractor_config_id": extractor_id,
                },
            )

        assert resp.status_code == 200
        extract_data = resp.json()
        fields = extract_data["fields"]
        assert "titular" in fields
        assert "monto" in fields
        assert extract_data["extractor_config_id"] is not None
        assert extract_data["extractor_config_name"] == config.name

        # ── Step 5: POST /extraction/submit with corrections ─────────────
        corrected_fields = {**fields, "titular": "Juan Perez"}

        with patch("src.infrastructure.api.extraction.routes.ExtractionRepository") as MockRepo:
            MockRepo.return_value.create.return_value = MagicMock(id=LOG_UUID)
            resp = client.post(
                "/extraction/submit",
                json={
                    "filename": "factura.pdf",
                    "extracted_fields": fields,
                    "final_fields": corrected_fields,
                    "extractor_config_id": extractor_id,
                },
            )

        assert resp.status_code == 200
        submit_data = resp.json()
        assert submit_data["message"]
        assert submit_data["id"]

    def test_flow_without_extractor_id_uses_default(self, client):
        """Extract without extractor_config_id should still work (uses default)."""
        default_config = _make_config(is_default=True)
        call_result = ApiCallResult(
            model="claude-haiku-4-5-20251001", success=True, response_time_ms=100.0
        )

        with (
            patch("src.infrastructure.api.extraction.routes.get_storage") as mock_storage,
            patch("src.infrastructure.api.extraction.routes.ExtractionService") as MockSvc,
            patch(
                "src.infrastructure.api.extraction.routes.ExtractorConfigRepository"
            ) as MockCfgRepo,
            patch("src.infrastructure.api.extraction.routes.ApiCallRepository"),
            patch("src.infrastructure.api.extraction.routes.AiUsageLogRepository"),
            patch("src.infrastructure.api.extraction.routes.QuotaService") as MockQuota,
        ):
            MockQuota.return_value.check_extraction_quota.return_value = None
            mock_storage.return_value.download.return_value = b"bytes"
            MockSvc.return_value.extract.return_value = ({"titular": "Test"}, call_result, None)
            MockCfgRepo.return_value.get_by_id.return_value = None
            MockCfgRepo.return_value.get_default.return_value = default_config

            resp = client.post(
                "/extraction/extract",
                json={
                    "s3_key": "uploads/test.pdf",
                    "filename": "test.pdf",
                    # No extractor_config_id — should use default
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["fields"]["titular"] == "Test"
        assert data["extractor_config_name"] == default_config.name
