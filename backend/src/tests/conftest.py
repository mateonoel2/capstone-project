import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.domain.entities import UserData
from src.infrastructure.auth import get_admin_user, get_current_user
from src.infrastructure.database import get_db
from src.main import app

USER_UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")
ADMIN_UUID = uuid.UUID("00000000-0000-0000-0000-000000000002")
GUEST_UUID = uuid.UUID("00000000-0000-0000-0000-000000000003")
CONFIG_UUID = uuid.UUID("00000000-0000-0000-0000-000000000010")
CONFIG_UUID_2 = uuid.UUID("00000000-0000-0000-0000-000000000011")
VERSION_UUID = uuid.UUID("00000000-0000-0000-0000-000000000020")
TOKEN_UUID = uuid.UUID("00000000-0000-0000-0000-000000000030")
TOKEN_UUID_2 = uuid.UUID("00000000-0000-0000-0000-000000000031")
LOG_UUID = uuid.UUID("00000000-0000-0000-0000-000000000040")


def make_user(
    role: str = "user",
    user_id: uuid.UUID = USER_UUID,
    is_active: bool = True,
    github_username: str = "testuser",
) -> UserData:
    return UserData(
        id=user_id,
        github_id=12345,
        github_username=github_username,
        email="test@example.com",
        avatar_url="https://github.com/avatar.png",
        role=role,
        is_active=is_active,
    )


@pytest.fixture()
def fake_user():
    return make_user(role="user", user_id=USER_UUID)


@pytest.fixture()
def fake_admin():
    return make_user(role="admin", user_id=ADMIN_UUID, github_username="adminuser")


@pytest.fixture()
def fake_guest():
    return make_user(role="guest", user_id=GUEST_UUID, github_username="guestuser")


@pytest.fixture()
def fake_db():
    return MagicMock()


@pytest.fixture(autouse=True, scope="session")
def _patch_lifespan():
    """Prevent lifespan from running migrations or touching S3."""
    with (
        patch("src.main.run_migrations"),
        patch("src.main.get_storage"),
    ):
        yield


@pytest.fixture()
def client(fake_user, fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_client(fake_admin, fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: fake_admin
    app.dependency_overrides[get_admin_user] = lambda: fake_admin
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def guest_client(fake_guest, fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: fake_guest
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def unauth_client(fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
