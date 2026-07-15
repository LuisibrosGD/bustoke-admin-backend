from time import time

from httpx import AsyncClient

pytestmark = __import__("pytest").mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"


def _unique_doc() -> str:
    return f"P{int(time() * 1_000_000) % 10_000_000_000}"


async def _login(client: AsyncClient) -> str:
    resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
    return resp.json()["accessToken"]


async def _create_pasajero(client: AsyncClient, token: str, doc: str) -> dict:
    body = {"idTipoDocumento": 1, "numeroDocumento": doc, "nombres": "Test", "apellidoPaterno": "Pasajero", "apellidoMaterno": "Prueba", "fechaNacimiento": "1990-01-01"}
    resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
    return resp.json()


class TestCreatePasajero:

    async def test_create_pasajero(self, client: AsyncClient):
        doc = _unique_doc()
        token = await _login(client)
        data = await _create_pasajero(client, token, doc)
        assert data.get("id")
        assert data["nombres"] == "Test"
        assert data["numeroDocumento"] == doc


class TestListPasajeros:

    async def test_list_all(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/pasajeros/all", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_by_viaje(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/1/pasajeros", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestGetPasajero:

    async def test_get_pasajero_by_id(self, client: AsyncClient):
        token = await _login(client)
        created = await _create_pasajero(client, token, _unique_doc())
        resp = await client.get(f"/admin/viajes/pasajeros/{created['id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_pasajero_not_found(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/pasajeros/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestUpdatePasajero:

    async def test_update_pasajero(self, client: AsyncClient):
        token = await _login(client)
        created = await _create_pasajero(client, token, _unique_doc())
        resp = await client.put(f"/admin/viajes/pasajeros/{created['id']}", json={"nombres": "Updated"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["nombres"] == "Updated"


class TestDeletePasajero:

    async def test_delete_pasajero(self, client: AsyncClient):
        token = await _login(client)
        created = await _create_pasajero(client, token, _unique_doc())
        resp = await client.delete(f"/admin/viajes/pasajeros/{created['id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
