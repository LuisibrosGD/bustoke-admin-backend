import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"


async def _login(client: AsyncClient) -> str:
    resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
    return resp.json()["accessToken"]


async def _create_viaje(client: AsyncClient, token: str) -> int:
    body = {"idRuta": 1, "idBus": 1, "fechaHoraSalida": "2026-08-10T08:00:00", "fechaHoraLlegada": "2026-08-10T12:00:00"}
    resp = await client.post("/admin/viajes/", json=body, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


async def _create_pasajero(client: AsyncClient, token: str, doc: str) -> int:
    body = {"idTipoDocumento": 1, "numeroDocumento": doc, "nombres": "Boleto", "apellidoPaterno": "Test", "apellidoMaterno": "Pasajero"}
    resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


class TestCreateBoleto:

    async def test_create_boleto(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550001")
        body = {
            "idViaje": viaje_id,
            "idPasajero": pasajero_id,
            "idAsiento": 1,
            "emailContacto": "test@example.com",
            "canal": "web",
            "codigoQr": f"QR-{viaje_id}-{pasajero_id}",
            "precioFinal": 50.00,
        }
        resp = await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["codigoQr"] == f"QR-{viaje_id}-{pasajero_id}"


class TestListBoletos:

    async def test_list_all(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/boletos/all", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_by_viaje(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550002")
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": 1, "emailContacto": "list@test.com", "canal": "web", "codigoQr": f"QR-LIST-{viaje_id}", "precioFinal": 30.00}
        await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        resp = await client.get(f"/admin/viajes/{viaje_id}/boletos", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1


class TestGetBoleto:

    async def test_get_boleto_by_id(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550003")
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": 1, "emailContacto": "get@test.com", "canal": "web", "codigoQr": f"QR-GET-{viaje_id}", "precioFinal": 40.00}
        create_resp = await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        boleto_id = create_resp.json()["id"]
        resp = await client.get(f"/admin/viajes/boletos/{boleto_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == boleto_id

    async def test_get_boleto_not_found(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/boletos/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestUpdateBoleto:

    async def test_update_boleto(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550004")
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": 1, "emailContacto": "update@test.com", "canal": "web", "codigoQr": f"QR-UPD-{viaje_id}", "precioFinal": 60.00}
        create_resp = await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        boleto_id = create_resp.json()["id"]
        resp = await client.put(f"/admin/viajes/boletos/{boleto_id}", json={"estado": "cancelado"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["estado"] == "cancelado"


class TestDeleteBoleto:

    async def test_delete_boleto(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550005")
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": 1, "emailContacto": "delete@test.com", "canal": "web", "codigoQr": f"QR-DEL-{viaje_id}", "precioFinal": 20.00}
        create_resp = await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        boleto_id = create_resp.json()["id"]
        resp = await client.delete(f"/admin/viajes/boletos/{boleto_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200


class TestCheckIn:

    async def test_checkin_boleto(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550006")
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": 1, "emailContacto": "checkin@test.com", "canal": "web", "codigoQr": f"QR-CK-{viaje_id}", "precioFinal": 35.00}
        create_resp = await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        boleto_id = create_resp.json()["id"]
        resp = await client.put(f"/admin/viajes/boletos/{boleto_id}/check-in", json={"estadoCheckin": "realizado"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["estadoCheckin"] == "realizado"


class TestScanQR:

    async def test_scan_qr_success(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token)
        pasajero_id = await _create_pasajero(client, token, "55550007")
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": 1, "emailContacto": "scan@test.com", "canal": "web", "codigoQr": f"QR-SCAN-{viaje_id}", "precioFinal": 45.00}
        await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        resp = await client.post(f"/admin/viajes/{viaje_id}/check-in/scan", json={"codigoQr": f"QR-SCAN-{viaje_id}"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["codigoQr"] == f"QR-SCAN-{viaje_id}"

    async def test_scan_qr_not_found(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.post("/admin/viajes/1/check-in/scan", json={"codigoQr": "QR-NO-EXISTE"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
