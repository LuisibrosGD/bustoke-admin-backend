import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"


class TestCreatePasajero:

    async def test_create_pasajero(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {
            "idTipoDocumento": 1,
            "numeroDocumento": "99999999",
            "nombres": "Test",
            "apellidoPaterno": "Pasajero",
            "apellidoMaterno": "Prueba",
            "fechaNacimiento": "1990-01-01",
        }
        resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombres"] == "Test"
        assert data["numeroDocumento"] == "99999999"
        assert "id" in data


class TestListPasajeros:

    async def test_list_all(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/pasajeros/all", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_by_viaje(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/1/pasajeros", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestGetPasajero:

    async def test_get_pasajero_by_id(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {"idTipoDocumento": 1, "numeroDocumento": "88888888", "nombres": "Get", "apellidoPaterno": "Test", "apellidoMaterno": "Pasajero"}
        create_resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
        pasajero_id = create_resp.json()["id"]
        resp = await client.get(f"/admin/viajes/pasajeros/{pasajero_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == pasajero_id

    async def test_get_pasajero_not_found(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/pasajeros/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestUpdatePasajero:

    async def test_update_pasajero(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {"idTipoDocumento": 1, "numeroDocumento": "77777777", "nombres": "Update", "apellidoPaterno": "Test", "apellidoMaterno": "Pasajero"}
        create_resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
        pasajero_id = create_resp.json()["id"]
        resp = await client.put(f"/admin/viajes/pasajeros/{pasajero_id}", json={"nombres": "Updated"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["nombres"] == "Updated"


class TestDeletePasajero:

    async def test_delete_pasajero(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {"idTipoDocumento": 1, "numeroDocumento": "66666666", "nombres": "Delete", "apellidoPaterno": "Test", "apellidoMaterno": "Pasajero"}
        create_resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
        pasajero_id = create_resp.json()["id"]
        resp = await client.delete(f"/admin/viajes/pasajeros/{pasajero_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
