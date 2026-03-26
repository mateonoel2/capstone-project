import uuid
from unittest.mock import patch

from src.tests.conftest import make_user

USER_UUID_10 = uuid.UUID("00000000-0000-0000-0000-00000000000a")


class TestGetMe:
    def test_returns_user_data(self, client, fake_user):
        resp = client.get("/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(fake_user.id)
        assert data["github_username"] == fake_user.github_username
        assert data["role"] == fake_user.role

    def test_unauth_returns_401(self, unauth_client):
        resp = unauth_client.get("/auth/me")
        assert resp.status_code in (401, 422)


class TestGetUsage:
    def test_guest_returns_quotas(self, guest_client):
        with (
            patch("src.infrastructure.api.auth.routes.ApiCallRepository") as MockApiCall,
            patch("src.infrastructure.api.auth.routes.ExtractorConfigRepository") as MockExtractor,
            patch("src.infrastructure.api.auth.routes.AiUsageLogRepository") as MockAi,
        ):
            MockApiCall.return_value.count_today.return_value = 2
            MockExtractor.return_value.count_by_user.return_value = 0
            MockAi.return_value.count_today.return_value = 1
            resp = guest_client.get("/auth/usage")
        assert resp.status_code == 200
        data = resp.json()
        assert data["unlimited"] is False
        assert data["extractions"]["used"] == 2

    def test_non_guest_returns_unlimited(self, client):
        with (
            patch("src.infrastructure.api.auth.routes.ApiCallRepository"),
            patch("src.infrastructure.api.auth.routes.ExtractorConfigRepository"),
            patch("src.infrastructure.api.auth.routes.AiUsageLogRepository"),
        ):
            resp = client.get("/auth/usage")
        assert resp.status_code == 200
        assert resp.json()["unlimited"] is True


class TestLogin:
    def test_login_creates_token(self, unauth_client):
        github_profile = {
            "id": 999,
            "login": "newuser",
            "email": "new@example.com",
            "avatar_url": "https://github.com/avatar.png",
        }
        user = make_user(user_id=USER_UUID_10, github_username="newuser")
        with (
            patch(
                "src.infrastructure.api.auth.routes.validate_github_token",
                return_value=github_profile,
            ),
            patch("src.infrastructure.api.auth.routes.UserRepository") as MockRepo,
            patch(
                "src.infrastructure.api.auth.routes.create_access_token",
                return_value="jwt-token-123",
            ),
        ):
            repo_instance = MockRepo.return_value
            repo_instance.get_by_github_id.return_value = None
            repo_instance.get_by_github_username.return_value = None
            repo_instance.create.return_value = user
            repo_instance.get_by_id.return_value = user

            resp = unauth_client.post("/auth/login", json={"github_access_token": "gh_token_123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "jwt-token-123"
        assert data["user"]["github_username"] == "newuser"
