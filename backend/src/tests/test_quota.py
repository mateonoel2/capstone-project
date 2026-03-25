from unittest.mock import MagicMock

import pytest

from src.domain.entities import QuotaExceededError, UserData
from src.domain.services.quota import (
    GUEST_DAILY_AI_PROMPTS,
    GUEST_DAILY_EXTRACTIONS,
    GUEST_MAX_EXTRACTORS,
    QuotaService,
)


def _make_user(role: str = "guest", user_id: int = 1) -> UserData:
    return UserData(
        id=user_id,
        github_id=None,
        github_username="testuser",
        email=None,
        avatar_url=None,
        role=role,
        is_active=True,
    )


def _make_service(
    extractions_today: int = 0,
    extractors_count: int = 0,
    ai_prompts_today: int = 0,
) -> QuotaService:
    api_call_repo = MagicMock()
    api_call_repo.count_today.return_value = extractions_today

    extractor_repo = MagicMock()
    extractor_repo.count_by_user.return_value = extractors_count

    ai_usage_repo = MagicMock()
    ai_usage_repo.count_today.return_value = ai_prompts_today

    return QuotaService(
        api_call_repo=api_call_repo,
        extractor_repo=extractor_repo,
        ai_usage_repo=ai_usage_repo,
    )


# --- Extraction quota ---


class TestExtractionQuota:
    def test_guest_under_limit_allowed(self):
        service = _make_service(extractions_today=GUEST_DAILY_EXTRACTIONS - 1)
        service.check_extraction_quota(_make_user("guest"))

    def test_guest_at_limit_raises(self):
        service = _make_service(extractions_today=GUEST_DAILY_EXTRACTIONS)
        with pytest.raises(QuotaExceededError):
            service.check_extraction_quota(_make_user("guest"))

    def test_guest_over_limit_raises(self):
        service = _make_service(extractions_today=GUEST_DAILY_EXTRACTIONS + 5)
        with pytest.raises(QuotaExceededError):
            service.check_extraction_quota(_make_user("guest"))

    def test_regular_user_no_limit(self):
        service = _make_service(extractions_today=1000)
        service.check_extraction_quota(_make_user("user"))

    def test_admin_no_limit(self):
        service = _make_service(extractions_today=1000)
        service.check_extraction_quota(_make_user("admin"))


# --- Extractor create quota ---


class TestExtractorCreateQuota:
    def test_guest_under_limit_allowed(self):
        service = _make_service(extractors_count=0)
        service.check_extractor_create_quota(_make_user("guest"))

    def test_guest_at_limit_raises(self):
        service = _make_service(extractors_count=GUEST_MAX_EXTRACTORS)
        with pytest.raises(QuotaExceededError):
            service.check_extractor_create_quota(_make_user("guest"))

    def test_regular_user_no_limit(self):
        service = _make_service(extractors_count=100)
        service.check_extractor_create_quota(_make_user("user"))


# --- AI prompt quota ---


class TestAiPromptQuota:
    def test_guest_under_limit_allowed(self):
        service = _make_service(ai_prompts_today=GUEST_DAILY_AI_PROMPTS - 1)
        service.check_ai_prompt_quota(_make_user("guest"))

    def test_guest_at_limit_raises(self):
        service = _make_service(ai_prompts_today=GUEST_DAILY_AI_PROMPTS)
        with pytest.raises(QuotaExceededError):
            service.check_ai_prompt_quota(_make_user("guest"))

    def test_regular_user_no_limit(self):
        service = _make_service(ai_prompts_today=1000)
        service.check_ai_prompt_quota(_make_user("user"))


# --- Usage report ---


class TestGetUsage:
    def test_guest_returns_limits(self):
        service = _make_service(extractions_today=3, extractors_count=1, ai_prompts_today=5)
        usage = service.get_usage(_make_user("guest"))

        assert usage["unlimited"] is False
        assert usage["extractions"] == {"used": 3, "limit": GUEST_DAILY_EXTRACTIONS}
        assert usage["extractors"] == {"used": 1, "limit": GUEST_MAX_EXTRACTORS}
        assert usage["ai_prompts"] == {"used": 5, "limit": GUEST_DAILY_AI_PROMPTS}

    def test_regular_user_unlimited(self):
        usage = _make_service().get_usage(_make_user("user"))
        assert usage == {"unlimited": True}

    def test_admin_unlimited(self):
        usage = _make_service().get_usage(_make_user("admin"))
        assert usage == {"unlimited": True}
