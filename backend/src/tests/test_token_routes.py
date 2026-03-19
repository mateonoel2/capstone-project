from unittest.mock import patch

from src.domain.entities import ApiTokenData
from src.infrastructure.auth import TOKEN_PREFIX


class TestCreateToken:
    def test_creates_token_with_prefix(self, client):
        api_token = ApiTokenData(id=1, user_id=1, name="test-token")
        with (
            patch("src.infrastructure.api.tokens.routes.generate_api_token") as mock_gen,
            patch("src.infrastructure.api.tokens.routes.hash_token", return_value="hashed"),
            patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo,
        ):
            mock_gen.return_value = f"{TOKEN_PREFIX}abc123"
            MockRepo.return_value.create.return_value = api_token
            resp = client.post("/tokens", json={"name": "test-token"})
        assert resp.status_code == 200
        assert resp.json()["token"].startswith(TOKEN_PREFIX)

    def test_guest_gets_403(self, guest_client):
        resp = guest_client.post("/tokens", json={"name": "test-token"})
        assert resp.status_code == 403


class TestListTokens:
    def test_lists_user_tokens(self, client):
        tokens = [
            ApiTokenData(id=1, user_id=1, name="token-a"),
            ApiTokenData(id=2, user_id=1, name="token-b"),
        ]
        with patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo:
            MockRepo.return_value.get_by_user.return_value = tokens
            resp = client.get("/tokens")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestRevokeToken:
    def test_revokes_token(self, client):
        with patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo:
            MockRepo.return_value.revoke.return_value = True
            resp = client.delete("/tokens/1")
        assert resp.status_code == 200

    def test_not_found_returns_404(self, client):
        with patch("src.infrastructure.api.tokens.routes.ApiTokenRepository") as MockRepo:
            MockRepo.return_value.revoke.return_value = False
            resp = client.delete("/tokens/999")
        assert resp.status_code == 404
