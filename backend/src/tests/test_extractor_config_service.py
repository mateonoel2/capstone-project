from unittest.mock import MagicMock

from src.domain.entities import ExtractorConfigData
from src.domain.services.extractor_config import ExtractorConfigService


def _make_config(**overrides):
    defaults = dict(
        id=1,
        name="test",
        description="",
        prompt="extract",
        model="test-model",
        output_schema={},
        is_default=False,
        status="active",
    )
    defaults.update(overrides)
    return ExtractorConfigData(**defaults)


def _make_service(configs=None):
    repo = MagicMock()
    repo.get_all.return_value = configs or []
    repo.create.side_effect = lambda data, **kw: data
    repo.update.side_effect = lambda config_id, data: data
    return ExtractorConfigService(repo), repo


class TestCreate:
    def test_draft_forces_is_default_false(self):
        service, repo = _make_service()
        data = _make_config(status="draft", is_default=True)
        result = service.create(data)
        assert result.is_default is False

    def test_is_default_clears_others(self):
        existing = _make_config(id=10, is_default=True)
        service, repo = _make_service(configs=[existing])
        data = _make_config(id=None, is_default=True, status="active")
        service.create(data)
        # Should have called update on the existing default to clear it
        repo.update.assert_any_call(10, existing)
        assert existing.is_default is False


class TestUpdate:
    def test_draft_forces_is_default_false(self):
        service, repo = _make_service()
        data = _make_config(id=1, status="draft", is_default=True)
        result = service.update(1, data)
        assert result.is_default is False

    def test_clears_others_except_self(self):
        other = _make_config(id=10, is_default=True)
        self_config = _make_config(id=1, is_default=True)
        service, repo = _make_service(configs=[other, self_config])
        data = _make_config(id=1, is_default=True, status="active")
        service.update(1, data)
        # other should have been cleared, self should not
        assert other.is_default is False


class TestClearDefault:
    def test_clears_all_except_excluded(self):
        c1 = _make_config(id=1, is_default=True)
        c2 = _make_config(id=2, is_default=True)
        c3 = _make_config(id=3, is_default=False)
        service, repo = _make_service(configs=[c1, c2, c3])
        service._clear_default(exclude_id=1)
        assert c1.is_default is True  # excluded
        assert c2.is_default is False  # cleared
