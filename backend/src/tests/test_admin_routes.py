from unittest.mock import patch

from src.tests.conftest import make_user


class TestListUsers:
    def test_admin_gets_users(self, admin_client):
        users = [make_user(user_id=1), make_user(user_id=2, github_username="other")]
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.get_all.return_value = users
            resp = admin_client.get("/admin/users")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_non_admin_gets_403(self, client):
        resp = client.get("/admin/users")
        assert resp.status_code == 403


class TestCreateUser:
    def test_creates_user(self, admin_client):
        new_user = make_user(user_id=10, github_username="newuser")
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_github_username.return_value = None
            MockRepo.return_value.create.return_value = new_user
            resp = admin_client.post(
                "/admin/users",
                json={"github_username": "newuser", "role": "user"},
            )
        assert resp.status_code == 201
        assert resp.json()["github_username"] == "newuser"

    def test_duplicate_returns_409(self, admin_client):
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.get_by_github_username.return_value = make_user()
            resp = admin_client.post(
                "/admin/users",
                json={"github_username": "testuser", "role": "user"},
            )
        assert resp.status_code == 409


class TestUpdateUser:
    def test_updates_user(self, admin_client):
        updated = make_user(user_id=5, role="admin")
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.update.return_value = updated
            resp = admin_client.put("/admin/users/5", json={"role": "admin"})
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    def test_not_found_returns_404(self, admin_client):
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.update.return_value = None
            resp = admin_client.put("/admin/users/999", json={"role": "user"})
        assert resp.status_code == 404


class TestDeleteUser:
    def test_deletes_user(self, admin_client, fake_admin):
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.delete.return_value = True
            resp = admin_client.delete("/admin/users/99")
        assert resp.status_code == 200

    def test_self_delete_returns_400(self, admin_client, fake_admin):
        resp = admin_client.delete(f"/admin/users/{fake_admin.id}")
        assert resp.status_code == 400

    def test_not_found_returns_404(self, admin_client):
        with patch("src.infrastructure.api.admin.routes.UserRepository") as MockRepo:
            MockRepo.return_value.delete.return_value = False
            resp = admin_client.delete("/admin/users/999")
        assert resp.status_code == 404
