import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"
ADMIN_EMAIL = "admin.cruz@cruzdelsur.com.pe"
ADMIN_PASS = "TempPassword123!1"


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestListAgencias:

    async def test_list_all_as_superadmin(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.get("/admin/agencias/", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_only_own_as_admin_agencia(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})).json()
        resp = await client.get("/admin/agencias/", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert "CRUZ DEL SUR" in items[0]["razonSocial"].upper()


class TestGetAgencia:

    async def test_get_agencia_by_id(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.get("/admin/agencias/1", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 200
        assert "razonSocial" in resp.json()

    async def test_get_agencia_not_found(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.get("/admin/agencias/99999", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 404


class TestCreateAgencia:

    async def _create(self, client: AsyncClient, ruc: str, name: str, token: str) -> dict:
        return (await client.post("/admin/agencias/", json={"ruc": ruc, "razonSocial": name}, headers={"Authorization": f"Bearer {token}"})).json()

    async def _delete(self, client: AsyncClient, id: int, token: str):
        await client.delete(f"/admin/agencias/{id}", headers={"Authorization": f"Bearer {token}"})

    async def test_create_as_superadmin(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        created = await self._create(client, "20999999991", "Agencia Test Crear", data["accessToken"])
        assert created.get("id")
        await self._delete(client, created["id"], data["accessToken"])

    async def test_create_as_admin_agencia_forbidden(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})).json()
        resp = await client.post("/admin/agencias/", json={"ruc": "20999999992", "razonSocial": "X"}, headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 403

    async def test_create_duplicate_ruc(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        created = await self._create(client, "20999999993", "Original", data["accessToken"])
        resp = await client.post("/admin/agencias/", json={"ruc": "20999999993", "razonSocial": "Duplicado"}, headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 409
        await self._delete(client, created["id"], data["accessToken"])


class TestUpdateAgencia:

    async def test_update_own_created_agencia(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        token = data["accessToken"]
        created = (await client.post("/admin/agencias/", json={"ruc": "20999999994", "razonSocial": "Para Update"}, headers={"Authorization": f"Bearer {token}"})).json()
        resp = await client.put(f"/admin/agencias/{created['id']}", json={"razonSocial": "Updated"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["razonSocial"] == "Updated"
        await client.delete(f"/admin/agencias/{created['id']}", headers={"Authorization": f"Bearer {token}"})

    async def test_update_not_found(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.put("/admin/agencias/99999", json={"razonSocial": "X"}, headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 404


class TestDeleteAgencia:

    async def test_delete_own_created_agencia(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        token = data["accessToken"]
        created = (await client.post("/admin/agencias/", json={"ruc": "20999999995", "razonSocial": "Para Delete"}, headers={"Authorization": f"Bearer {token}"})).json()
        resp = await client.delete(f"/admin/agencias/{created['id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_delete_not_found(self, client: AsyncClient):
        data = (await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})).json()
        resp = await client.delete("/admin/agencias/99999", headers={"Authorization": f"Bearer {data['accessToken']}"})
        assert resp.status_code == 404
