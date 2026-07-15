import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"


class TestListViajes:

    async def test_list_all(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_with_pagination(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/?skip=0&limit=5", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestCreateViaje:

    async def test_create_viaje(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {
            "idRuta": 1,
            "idBus": 1,
            "idChofer": 1,
            "fechaHoraSalida": "2026-08-01T08:00:00",
            "fechaHoraLlegada": "2026-08-01T12:00:00",
            "estado": "programado",
        }
        resp = await client.post("/admin/viajes/", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
        assert resp.json()["estado"] == "programado"


class TestGetViaje:

    async def test_get_viaje_by_id(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {"idRuta": 1, "idBus": 1, "fechaHoraSalida": "2026-08-02T08:00:00", "fechaHoraLlegada": "2026-08-02T12:00:00"}
        create_resp = await client.post("/admin/viajes/", json=body, headers={"Authorization": f"Bearer {token}"})
        viaje_id = create_resp.json()["id"]
        resp = await client.get(f"/admin/viajes/{viaje_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == viaje_id

    async def test_get_viaje_not_found(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestUpdateViaje:

    async def test_update_viaje(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {"idRuta": 1, "idBus": 1, "fechaHoraSalida": "2026-08-03T08:00:00", "fechaHoraLlegada": "2026-08-03T12:00:00"}
        create_resp = await client.post("/admin/viajes/", json=body, headers={"Authorization": f"Bearer {token}"})
        viaje_id = create_resp.json()["id"]
        resp = await client.put(f"/admin/viajes/{viaje_id}", json={"estado": "en_curso"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["estado"] == "en_curso"

    async def test_update_not_found(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.put("/admin/viajes/99999", json={"estado": "cancelado"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestDeleteViaje:

    async def test_delete_viaje(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        body = {"idRuta": 1, "idBus": 1, "fechaHoraSalida": "2026-08-04T08:00:00", "fechaHoraLlegada": "2026-08-04T12:00:00"}
        create_resp = await client.post("/admin/viajes/", json=body, headers={"Authorization": f"Bearer {token}"})
        viaje_id = create_resp.json()["id"]
        resp = await client.delete(f"/admin/viajes/{viaje_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    async def test_delete_not_found(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.delete("/admin/viajes/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestFilterViajes:

    async def test_filter_by_bus(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/?id_bus=1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_filter_by_ruta(self, client: AsyncClient):
        login_resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
        token = login_resp.json()["accessToken"]
        resp = await client.get("/admin/viajes/?id_ruta=1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
