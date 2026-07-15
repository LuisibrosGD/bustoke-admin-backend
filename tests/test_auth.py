import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"
ADMIN_EMAIL = "admin.cruz@cruzdelsur.com.pe"
ADMIN_PASS = "TempPassword123!1"


class TestLogin:

    async def test_login_superadmin_success(self, client: AsyncClient):
        resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        assert resp.status_code == 200
        data = resp.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["tokenType"] == "bearer"
        assert data["rol"] == "superadmin"

    async def test_login_admin_agencia_success(self, client: AsyncClient):
        resp = await client.post("/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "admin_agencia"
        assert data["idAgencia"] == 1

    async def test_login_invalid_credentials(self, client: AsyncClient):
        resp = await client.post("/admin/auth/login", json={"email": "noexiste@test.com", "password": "wrongpass"})
        assert resp.status_code == 401

    async def test_login_wrong_password(self, client: AsyncClient):
        resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": "wrongpassword"})
        assert resp.status_code == 401


class TestRefresh:

    async def _login(self, client: AsyncClient) -> dict:
        return (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()

    async def test_refresh_success(self, client: AsyncClient):
        data = await self._login(client)
        resp = await client.post("/admin/auth/refresh", json={"refreshToken": data["refreshToken"]})
        assert resp.status_code == 200
        assert "accessToken" in resp.json()
        assert "refreshToken" in resp.json()

    async def test_refresh_invalid_token(self, client: AsyncClient):
        resp = await client.post("/admin/auth/refresh", json={"refreshToken": "token-invalido"})
        assert resp.status_code == 401

    async def test_refresh_with_access_token(self, client: AsyncClient):
        data = await self._login(client)
        resp = await client.post("/admin/auth/refresh", json={"refreshToken": data["accessToken"]})
        assert resp.status_code == 401


class TestLogout:

    async def test_logout_success(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.post("/admin/auth/logout", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Sesión cerrada correctamente"

    async def test_logout_session_success(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.post("/admin/auth/logout-session", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 200


class TestForgotPassword:

    async def test_forgot_password_existing_email(self, client: AsyncClient):
        resp = await client.post("/admin/auth/forgot-password", json={"email": SUPERADMIN_EMAIL})
        assert resp.status_code == 200

    async def test_forgot_password_nonexistent_email(self, client: AsyncClient):
        resp = await client.post("/admin/auth/forgot-password", json={"email": "noexiste@test.com"})
        assert resp.status_code == 200


class TestResetPassword:

    async def test_reset_password_success(self, client: AsyncClient):
        from app.core.security import create_access_token
        reset_token = create_access_token({"sub": "5", "type": "password_reset"})
        resp = await client.post("/admin/auth/reset-password", json={"token": reset_token, "newPassword": SUPERADMIN_PASS})
        assert resp.status_code == 200

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        resp = await client.post("/admin/auth/reset-password", json={"token": "token-invalido", "newPassword": "x"})
        assert resp.status_code == 400


class TestRecoverEmail:

    async def test_recover_email(self, client: AsyncClient):
        resp = await client.post("/admin/auth/recover-email", json={"email": SUPERADMIN_EMAIL})
        assert resp.status_code == 200


class TestGetUsuario:

    async def test_get_usuario_success(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.get("/admin/auth/usuarios/5", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 200
        assert resp.json()["idUsuario"] == 5
        assert resp.json()["email"] == SUPERADMIN_EMAIL

    async def test_get_usuario_not_found(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.get("/admin/auth/usuarios/99999", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 404
