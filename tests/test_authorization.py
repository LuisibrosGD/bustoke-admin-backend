import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"
ADMIN_EMAIL = "admin.cruz@cruzdelsur.com.pe"
ADMIN_PASS = "TempPassword123!1"


async def superadmin_token(client: AsyncClient) -> str:
    resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
    return resp.json()["accessToken"]


async def admin_token(client: AsyncClient) -> str:
    resp = await client.post("/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    return resp.json()["accessToken"]


async def admin_refresh_token(client: AsyncClient) -> str:
    resp = await client.post("/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    return resp.json()["refreshToken"]


class TestNoToken:

    async def test_endpoint_without_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/admin/agencias/")
        assert resp.status_code == 401

    async def test_endpoint_without_token_on_create(self, client: AsyncClient):
        resp = await client.post("/admin/agencias/", json={"ruc": "20123456789", "razonSocial": "Test"})
        assert resp.status_code == 401


class TestInvalidToken:

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/admin/agencias/", headers={"Authorization": "Bearer token-invalido"})
        assert resp.status_code == 401

    async def test_malformed_header_returns_401(self, client: AsyncClient):
        resp = await client.get("/admin/agencias/", headers={"Authorization": "NotBearer xyz"})
        assert resp.status_code == 401


class TestRefreshTokenAsAccess:

    async def test_refresh_token_as_access_returns_401(self, client: AsyncClient):
        refresh = await admin_refresh_token(client)
        resp = await client.get("/admin/agencias/", headers={"Authorization": f"Bearer {refresh}"})
        assert resp.status_code == 401


class TestRoleForbidden:

    async def test_admin_agencia_cannot_create_agencia(self, client: AsyncClient):
        token = await admin_token(client)
        resp = await client.post(
            "/admin/agencias/",
            json={"ruc": "20123456788", "razonSocial": "No Permitido"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    async def test_admin_agencia_cannot_update_agencia(self, client: AsyncClient):
        token = await admin_token(client)
        resp = await client.put(
            "/admin/agencias/1",
            json={"razonSocial": "Hackeado"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    async def test_admin_agencia_cannot_delete_agencia(self, client: AsyncClient):
        token = await admin_token(client)
        resp = await client.delete("/admin/agencias/1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


class TestSuperadminAccess:

    async def test_superadmin_can_list_agencias(self, client: AsyncClient):
        token = await superadmin_token(client)
        resp = await client.get("/admin/agencias/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_superadmin_can_create_agencia(self, client: AsyncClient):
        token = await superadmin_token(client)
        resp = await client.post(
            "/admin/agencias/",
            json={"ruc": "20988888888", "razonSocial": "Superadmin Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
