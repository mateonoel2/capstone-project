from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException

from src.infrastructure.auth import (
    JWT_ALGORITHM,
    JWT_SECRET,
    TOKEN_PREFIX,
    _authenticate_jwt,
    create_access_token,
    generate_api_token,
    get_current_user,
    hash_token,
)
from src.tests.conftest import make_user


class TestCreateAccessToken:
    def test_valid_jwt_with_correct_claims(self):
        user = make_user(role="user", user_id=42)
        token = create_access_token(user)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["user_id"] == 42
        assert payload["role"] == "user"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_has_24h_expiry(self):
        user = make_user()
        token = create_access_token(user)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        delta = exp - iat
        assert timedelta(hours=23, minutes=59) < delta <= timedelta(hours=24, minutes=1)


class TestHashToken:
    def test_deterministic(self):
        assert hash_token("abc123") == hash_token("abc123")

    def test_different_inputs_different_hashes(self):
        assert hash_token("token_a") != hash_token("token_b")


class TestGenerateApiToken:
    def test_starts_with_prefix(self):
        token = generate_api_token()
        assert token.startswith(TOKEN_PREFIX)

    def test_two_calls_are_unique(self):
        assert generate_api_token() != generate_api_token()


class TestAuthenticateJwt:
    def _make_token(self, user_id=1, role="user", expired=False):
        exp = datetime.now(timezone.utc) + (timedelta(hours=-1) if expired else timedelta(hours=24))
        payload = {"user_id": user_id, "role": role, "exp": exp, "iat": datetime.now(timezone.utc)}
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def test_valid_token_returns_user(self):
        token = self._make_token(user_id=5)
        db = MagicMock()
        user = make_user(user_id=5)
        with patch("src.infrastructure.auth.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_id.return_value = user
            result = _authenticate_jwt(token, db)
        assert result.id == 5

    def test_expired_token_raises_401(self):
        token = self._make_token(expired=True)
        with pytest.raises(HTTPException) as exc_info:
            _authenticate_jwt(token, MagicMock())
        assert exc_info.value.status_code == 401

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            _authenticate_jwt("not-a-jwt", MagicMock())
        assert exc_info.value.status_code == 401

    def test_inactive_user_raises_403(self):
        token = self._make_token(user_id=5)
        db = MagicMock()
        user = make_user(user_id=5, is_active=False)
        with patch("src.infrastructure.auth.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_id.return_value = user
            with pytest.raises(HTTPException) as exc_info:
                _authenticate_jwt(token, db)
        assert exc_info.value.status_code == 403


class TestGetCurrentUser:
    def test_missing_bearer_prefix_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="Token abc", db=MagicMock())
        assert exc_info.value.status_code == 401

    def test_non_exto_routes_to_jwt(self):
        token = "some-jwt-token"
        db = MagicMock()
        user = make_user()
        with patch("src.infrastructure.auth._authenticate_jwt", return_value=user) as mock_jwt:
            result = get_current_user(authorization=f"Bearer {token}", db=db)
        mock_jwt.assert_called_once_with(token, db)
        assert result == user

    def test_exto_routes_to_api_token(self):
        token = "exto_abc123"
        db = MagicMock()
        user = make_user()
        with patch(
            "src.infrastructure.auth._authenticate_api_token", return_value=user
        ) as mock_api:
            result = get_current_user(authorization=f"Bearer {token}", db=db)
        mock_api.assert_called_once_with(token, db)
        assert result == user
