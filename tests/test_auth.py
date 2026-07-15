import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"
ADMIN_EMAIL = "admin.cruz@cruzdelsur.com.pe"
ADMIN_PASS = "TempPassword123!1"


async def login(client: AsyncClient, email: str, password: str) -> dict:
    resp = await client.post("/admin/auth/login", json={"email": email, "password": password})
    return resp


class TestLogin:

    async def test_login_superadmin_success(self, client: AsyncClient):
        resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        assert resp.status_code == 200
        data = resp.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["tokenType"] == "bearer"
        assert data["rol"] == "superadmin"
        assert data["idUsuario"] == 5

    async def test_login_admin_agencia_success(self, client: AsyncClient):
        resp = await login(client, ADMIN_EMAIL, ADMIN_PASS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "admin_agencia"
        assert data["idAgencia"] == 1

    async def test_login_invalid_credentials(self, client: AsyncClient):
        resp = await login(client, "noexiste@test.com", "wrongpass")
        assert resp.status_code == 401

    async def test_login_wrong_password(self, client: AsyncClient):
        resp = await login(client, SUPERADMIN_EMAIL, "wrongpassword")
        assert resp.status_code == 401


class TestRefresh:

    async def test_refresh_success(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        refresh_token = login_resp.json()["refreshToken"]

        resp = await client.post("/admin/auth/refresh", json={"refreshToken": refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert "accessToken" in data
        assert "refreshToken" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        resp = await client.post("/admin/auth/refresh", json={"refreshToken": "token-invalido"})
        assert resp.status_code == 401

    async def test_refresh_with_access_token(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        access_token = login_resp.json()["accessToken"]

        resp = await client.post("/admin/auth/refresh", json={"refreshToken": access_token})
        assert resp.status_code == 401


class TestLogout:

    async def test_logout_success(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        token = login_resp.json()["accessToken"]

        resp = await client.post("/admin/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Sesión cerrada correctamente"

    async def test_logout_session_success(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        token = login_resp.json()["accessToken"]

        resp = await client.post("/admin/auth/logout-session", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Todas las sesiones cerradas correctamente"


class TestForgotPassword:

    async def test_forgot_password_existing_email(self, client: AsyncClient):
        resp = await client.post("/admin/auth/forgot-password", json={"email": SUPERADMIN_EMAIL})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Si el correo existe, recibirás instrucciones de recuperación"

    async def test_forgot_password_nonexistent_email(self, client: AsyncClient):
        resp = await client.post("/admin/auth/forgot-password", json={"email": "noexiste@test.com"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Si el correo existe, recibirás instrucciones de recuperación"


class TestResetPassword:

    async def test_reset_password_success(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        token = login_resp.json()["accessToken"]

        resp = await client.post("/admin/auth/reset-password", json={"token": token, "newPassword": "NewPass123!"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Contraseña restablecida correctamente"

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        resp = await client.post("/admin/auth/reset-password", json={"token": "token-invalido", "newPassword": "NewPass123!"})
        assert resp.status_code == 400


class TestRecoverEmail:

    async def test_recover_email(self, client: AsyncClient):
        resp = await client.post("/admin/auth/recover-email", json={"email": SUPERADMIN_EMAIL})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Si el correo existe, recibirás un enlace de recuperación"


class TestGetUsuario:

    async def test_get_usuario_success(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        token = login_resp.json()["accessToken"]

        resp = await client.get("/admin/auth/usuarios/5", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["idUsuario"] == 5
        assert data["email"] == SUPERADMIN_EMAIL
        assert data["rol"] == "superadmin"

    async def test_get_usuario_not_found(self, client: AsyncClient):
        login_resp = await login(client, SUPERADMIN_EMAIL, SUPERADMIN_PASS)
        token = login_resp.json()["accessToken"]

        resp = await client.get("/admin/auth/usuarios/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
