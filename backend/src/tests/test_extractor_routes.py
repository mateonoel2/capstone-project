import uuid
from unittest.mock import patch

from src.domain.entities import ExtractorConfigData, QuotaExceededError
from src.tests.conftest import CONFIG_UUID, CONFIG_UUID_2, USER_UUID

CONFIG_UUID_5 = uuid.UUID("00000000-0000-0000-0000-000000000015")
CONFIG_UUID_999 = uuid.UUID("00000000-0000-0000-0000-000000000999")


def _make_config(**overrides):
    defaults = dict(
        id=CONFIG_UUID,
        name="test-extractor",
        description="A test extractor",
        prompt="Extract fields",
        model="claude-haiku-4-5-20251001",
        output_schema={"type": "object", "properties": {"name": {"type": "string"}}},
        is_default=False,
        status="active",
        user_id=USER_UUID,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )
    defaults.update(overrides)
    return ExtractorConfigData(**defaults)


class TestListExtractorConfigs:
    def test_lists_configs(self, client):
        configs = [_make_config(id=CONFIG_UUID), _make_config(id=CONFIG_UUID_2, name="other")]
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_all.return_value = configs
            resp = client.get("/extractors")
        assert resp.status_code == 200
        assert len(resp.json()["configs"]) == 2


class TestGetAvailableModels:
    def test_returns_models(self, client):
        resp = client.get("/extractors/models")
        assert resp.status_code == 200
        models = resp.json()
        assert len(models) > 0
        assert any(m["id"] == "claude-haiku-4-5-20251001" for m in models)


class TestCreateExtractorConfig:
    def test_creates_config(self, client):
        config = _make_config(id=CONFIG_UUID_5)
        with (
            patch("src.infrastructure.api.extractors.routes.ExtractorConfigRepository") as MockRepo,
            patch("src.infrastructure.api.extractors.routes.ApiCallRepository"),
            patch("src.infrastructure.api.extractors.routes.AiUsageLogRepository"),
            patch("src.infrastructure.api.extractors.routes.QuotaService") as MockQuota,
        ):
            MockQuota.return_value.check_extractor_create_quota.return_value = None
            MockRepo.return_value.get_all.return_value = []
            MockRepo.return_value.create.return_value = config
            resp = client.post(
                "/extractors",
                json={
                    "name": "test-extractor",
                    "description": "A test",
                    "prompt": "Extract",
                    "model": "claude-haiku-4-5-20251001",
                    "output_schema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                    "is_default": False,
                    "status": "active",
                },
            )
        assert resp.status_code == 201
        assert resp.json()["name"] == "test-extractor"

    def test_guest_quota_returns_429(self, guest_client):
        with (
            patch("src.infrastructure.api.extractors.routes.ExtractorConfigRepository"),
            patch("src.infrastructure.api.extractors.routes.ApiCallRepository"),
            patch("src.infrastructure.api.extractors.routes.AiUsageLogRepository"),
            patch("src.infrastructure.api.extractors.routes.QuotaService") as MockQuota,
        ):
            MockQuota.return_value.check_extractor_create_quota.side_effect = QuotaExceededError(
                "Límite alcanzado"
            )
            resp = guest_client.post(
                "/extractors",
                json={
                    "name": "test",
                    "description": "test",
                    "prompt": "Extract",
                    "model": "claude-haiku-4-5-20251001",
                    "output_schema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                    "is_default": False,
                    "status": "active",
                },
            )
        assert resp.status_code == 429


class TestUpdateExtractorConfig:
    def test_updates_config(self, client):
        existing = _make_config(id=CONFIG_UUID)
        updated = _make_config(id=CONFIG_UUID, name="updated-name")
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = existing
            MockRepo.return_value.get_all.return_value = []
            MockRepo.return_value.update.return_value = updated
            resp = client.put(
                f"/extractors/{CONFIG_UUID}",
                json={"name": "updated-name"},
            )
        assert resp.status_code == 200
        assert resp.json()["name"] == "updated-name"

    def test_not_found_returns_404(self, client):
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = None
            resp = client.put(f"/extractors/{CONFIG_UUID_999}", json={"name": "x"})
        assert resp.status_code == 404


class TestDeleteExtractorConfig:
    def test_deletes_config(self, client):
        config = _make_config(id=CONFIG_UUID, is_default=False)
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = config
            MockRepo.return_value.delete.return_value = True
            resp = client.delete(f"/extractors/{CONFIG_UUID}")
        assert resp.status_code == 200

    def test_default_config_returns_400(self, client):
        config = _make_config(id=CONFIG_UUID, is_default=True)
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = config
            resp = client.delete(f"/extractors/{CONFIG_UUID}")
        assert resp.status_code == 400

    def test_not_found_returns_404(self, client):
        with patch(
            "src.infrastructure.api.extractors.routes.ExtractorConfigRepository"
        ) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = None
            resp = client.delete(f"/extractors/{CONFIG_UUID_999}")
        assert resp.status_code == 404
