from src.domain.entities import QuotaExceededError, UserData
from src.infrastructure.repository import (
    AiUsageLogRepository,
    ApiCallRepository,
    ExtractorConfigRepository,
)

GUEST_DAILY_EXTRACTIONS = 10
GUEST_MAX_EXTRACTORS = 1
GUEST_DAILY_AI_PROMPTS = 10


class QuotaService:
    def __init__(
        self,
        api_call_repo: ApiCallRepository,
        extractor_repo: ExtractorConfigRepository,
        ai_usage_repo: AiUsageLogRepository,
    ):
        self.api_call_repo = api_call_repo
        self.extractor_repo = extractor_repo
        self.ai_usage_repo = ai_usage_repo

    @staticmethod
    def _is_guest(user: UserData) -> bool:
        return user.role == "guest"

    def check_extraction_quota(self, user: UserData) -> None:
        if not self._is_guest(user):
            return
        count = self.api_call_repo.count_today(user.id)
        if count >= GUEST_DAILY_EXTRACTIONS:
            limit = GUEST_DAILY_EXTRACTIONS
            raise QuotaExceededError(f"Límite diario de extracciones alcanzado ({limit}/{limit})")

    def check_extractor_create_quota(self, user: UserData) -> None:
        if not self._is_guest(user):
            return
        count = self.extractor_repo.count_by_user(user.id)
        if count >= GUEST_MAX_EXTRACTORS:
            raise QuotaExceededError(
                f"Límite de extractores alcanzado ({GUEST_MAX_EXTRACTORS}/{GUEST_MAX_EXTRACTORS})"
            )

    def check_ai_prompt_quota(self, user: UserData) -> None:
        if not self._is_guest(user):
            return
        count = self.ai_usage_repo.count_today(user.id)
        if count >= GUEST_DAILY_AI_PROMPTS:
            limit = GUEST_DAILY_AI_PROMPTS
            raise QuotaExceededError(f"Límite diario de prompts IA alcanzado ({limit}/{limit})")

    def get_usage(self, user: UserData) -> dict:
        if not self._is_guest(user):
            return {"unlimited": True}
        return {
            "unlimited": False,
            "extractions": {
                "used": self.api_call_repo.count_today(user.id),
                "limit": GUEST_DAILY_EXTRACTIONS,
            },
            "extractors": {
                "used": self.extractor_repo.count_by_user(user.id),
                "limit": GUEST_MAX_EXTRACTORS,
            },
            "ai_prompts": {
                "used": self.ai_usage_repo.count_today(user.id),
                "limit": GUEST_DAILY_AI_PROMPTS,
            },
        }
