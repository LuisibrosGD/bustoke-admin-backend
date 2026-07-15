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


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


class TestListAgencias:

    async def test_list_all_as_superadmin(self, client: AsyncClient):
        token = await superadmin_token(client)
        resp = await client.get("/admin/agencias/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_list_only_own_as_admin_agencia(self, client: AsyncClient):
        token = await admin_token(client)
        resp = await client.get("/admin/agencias/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["razonSocial"] == "Cruz del Sur"


class TestGetAgencia:

    async def test_get_agencia_by_id(self, client: AsyncClient):
        token = await superadmin_token(client)
        resp = await client.get("/admin/agencias/1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert "razonSocial" in data
        assert "ruc" in data

    async def test_get_agencia_not_found(self, client: AsyncClient):
        token = await superadmin_token(client)
        resp = await client.get("/admin/agencias/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestCreateAgencia:

    async def test_create_as_superadmin(self, client: AsyncClient):
        token = await superadmin_token(client)
        body = {
            "ruc": "20999999999",
            "razonSocial": "Agencia Test",
            "estado": "activa",
        }
        resp = await client.post("/admin/agencias/", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["razonSocial"] == "Agencia Test"
        assert data["ruc"] == "20999999999"

    async def test_create_as_admin_agencia_forbidden(self, client: AsyncClient):
        token = await admin_token(client)
        body = {
            "ruc": "20999999998",
            "razonSocial": "Agencia Prohibida",
            "estado": "activa",
        }
        resp = await client.post("/admin/agencias/", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    async def test_create_duplicate_ruc(self, client: AsyncClient):
        token = await superadmin_token(client)
        body = {
            "ruc": "20999999999",
            "razonSocial": "Agencia Duplicada",
            "estado": "activa",
        }
        resp = await client.post("/admin/agencias/", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 409


class TestUpdateAgencia:

    async def test_update_as_superadmin(self, client: AsyncClient):
        token = await superadmin_token(client)
        body = {"razonSocial": "Agencia Test Modificada"}
        resp = await client.put("/admin/agencias/1", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["razonSocial"] == "Agencia Test Modificada"

    async def test_update_not_found(self, client: AsyncClient):
        token = await superadmin_token(client)
        body = {"razonSocial": "No Existe"}
        resp = await client.put("/admin/agencias/99999", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestDeleteAgencia:

    async def test_delete_as_superadmin(self, client: AsyncClient):
        token = await superadmin_token(client)
        body = {
            "ruc": "20999999997",
            "razonSocial": "Agencia a Eliminar",
            "estado": "activa",
        }
        create_resp = await client.post("/admin/agencias/", json=body, headers={"Authorization": f"Bearer {token}"})
        agencia_id = create_resp.json()["id"]

        resp = await client.delete(f"/admin/agencias/{agencia_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_delete_not_found(self, client: AsyncClient):
        token = await superadmin_token(client)
        resp = await client.delete("/admin/agencias/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
