from unittest.mock import MagicMock

import pytest

from src.domain.entities import QuotaExceededError
from src.domain.services.quota import (
    GUEST_DAILY_AI_PROMPTS,
    GUEST_DAILY_EXTRACTIONS,
    GUEST_MAX_EXTRACTORS,
    QuotaService,
)
from src.tests.conftest import make_user


def _make_service(
    api_call_count=0,
    extractor_count=0,
    ai_count=0,
) -> QuotaService:
    api_call_repo = MagicMock()
    api_call_repo.count_today.return_value = api_call_count
    extractor_repo = MagicMock()
    extractor_repo.count_by_user.return_value = extractor_count
    ai_usage_repo = MagicMock()
    ai_usage_repo.count_today.return_value = ai_count
    return QuotaService(api_call_repo, extractor_repo, ai_usage_repo)


class TestCheckExtractionQuota:
    def test_non_guest_bypasses(self):
        service = _make_service(api_call_count=999)
        service.check_extraction_quota(make_user(role="user"))  # no error

    def test_guest_under_limit_ok(self):
        service = _make_service(api_call_count=GUEST_DAILY_EXTRACTIONS - 1)
        service.check_extraction_quota(make_user(role="guest"))  # no error

    def test_guest_at_limit_raises(self):
        service = _make_service(api_call_count=GUEST_DAILY_EXTRACTIONS)
        with pytest.raises(QuotaExceededError):
            service.check_extraction_quota(make_user(role="guest"))


class TestCheckExtractorCreateQuota:
    def test_non_guest_bypasses(self):
        service = _make_service(extractor_count=999)
        service.check_extractor_create_quota(make_user(role="admin"))

    def test_guest_under_limit_ok(self):
        service = _make_service(extractor_count=GUEST_MAX_EXTRACTORS - 1)
        service.check_extractor_create_quota(make_user(role="guest"))

    def test_guest_at_limit_raises(self):
        service = _make_service(extractor_count=GUEST_MAX_EXTRACTORS)
        with pytest.raises(QuotaExceededError):
            service.check_extractor_create_quota(make_user(role="guest"))


class TestCheckAiPromptQuota:
    def test_non_guest_bypasses(self):
        service = _make_service(ai_count=999)
        service.check_ai_prompt_quota(make_user(role="user"))

    def test_guest_at_limit_raises(self):
        service = _make_service(ai_count=GUEST_DAILY_AI_PROMPTS)
        with pytest.raises(QuotaExceededError):
            service.check_ai_prompt_quota(make_user(role="guest"))


class TestGetUsage:
    def test_non_guest_returns_unlimited(self):
        service = _make_service()
        result = service.get_usage(make_user(role="user"))
        assert result == {"unlimited": True}

    def test_guest_returns_usage_breakdown(self):
        service = _make_service(api_call_count=3, extractor_count=1, ai_count=5)
        result = service.get_usage(make_user(role="guest"))
        assert result["unlimited"] is False
        assert result["extractions"]["used"] == 3
        assert result["extractions"]["limit"] == GUEST_DAILY_EXTRACTIONS
        assert result["extractors"]["used"] == 1
        assert result["ai_prompts"]["used"] == 5
