from time import time

from httpx import AsyncClient

pytestmark = __import__("pytest").mark.asyncio

SUPERADMIN_EMAIL = "sebastian.admin@bustoke.pe"
SUPERADMIN_PASS = "TempPassword123!5"


def _unique_doc() -> str:
    return f"B{int(time() * 1_000_000) % 10_000_000_000}"


async def _login(client: AsyncClient) -> str:
    resp = await client.post("/admin/auth/login", json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASS})
    return resp.json()["accessToken"]


async def _create_viaje(client: AsyncClient, token: str, hora: str) -> int:
    body = {"idRuta": 1, "idBus": 1, "fechaHoraSalida": f"2026-10-01T{hora}", "fechaHoraLlegada": f"2026-10-01T{int(hora[:2])+4:02d}:00:00"}
    resp = await client.post("/admin/viajes/", json=body, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


async def _create_pasajero(client: AsyncClient, token: str, doc: str) -> int:
    body = {"idTipoDocumento": 1, "numeroDocumento": doc, "nombres": "BoletoTest", "apellidoPaterno": "P", "apellidoMaterno": "M"}
    resp = await client.post("/admin/viajes/pasajeros", json=body, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


_asiento_counter = 0


async def _create_asiento(client: AsyncClient, token: str, bus_id: int = 1) -> int:
    global _asiento_counter
    _asiento_counter += 1
    n = _asiento_counter
    ts = int(time() * 1000) % 100_000
    body = {"idBus": bus_id, "numeroAsiento": f"A1-{ts}_{n}", "fila": "A", "piso": 1, "tipoServicio": "normal", "coordX": n, "coordY": n}
    resp = await client.post("/admin/flota/asientos", json=body, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


class TestCreateBoleto:

    async def test_create_boleto(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token, "08:00:00")
        asiento_id = await _create_asiento(client, token)
        doc = _unique_doc()
        pasajero_id = await _create_pasajero(client, token, doc)
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": asiento_id, "emailContacto": "a@b.com", "canal": "ventanilla_fisica", "codigoQr": f"QR-B1-{viaje_id}", "precioFinal": 50}
        resp = await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
        assert resp.json()["id"]


class TestListBoletos:

    async def test_list_all(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/boletos/all", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestGetBoleto:

    async def test_get_boleto_not_found(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.get("/admin/viajes/boletos/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


class TestCheckIn:

    async def test_checkin_boleto(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token, "09:00:00")
        asiento_id = await _create_asiento(client, token)
        doc = _unique_doc()
        pasajero_id = await _create_pasajero(client, token, doc)
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": asiento_id, "emailContacto": "ck@b.com", "canal": "ventanilla_fisica", "codigoQr": f"QR-CK-{viaje_id}", "precioFinal": 35}
        created = (await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})).json()
        resp = await client.put(f"/admin/viajes/boletos/{created['id']}/check-in", json={"estadoCheckin": "realizado"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["estadoCheckin"] == "realizado"


class TestScanQR:

    async def test_scan_qr_success(self, client: AsyncClient):
        token = await _login(client)
        viaje_id = await _create_viaje(client, token, "10:00:00")
        asiento_id = await _create_asiento(client, token)
        doc = _unique_doc()
        pasajero_id = await _create_pasajero(client, token, doc)
        body = {"idViaje": viaje_id, "idPasajero": pasajero_id, "idAsiento": asiento_id, "emailContacto": "qr@b.com", "canal": "ventanilla_fisica", "codigoQr": f"QR-SC-{viaje_id}", "precioFinal": 45}
        await client.post("/admin/viajes/boletos", json=body, headers={"Authorization": f"Bearer {token}"})
        resp = await client.post(f"/admin/viajes/{viaje_id}/check-in/scan", json={"codigoQr": f"QR-SC-{viaje_id}"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["codigoQr"] == f"QR-SC-{viaje_id}"

    async def test_scan_qr_not_found(self, client: AsyncClient):
        token = await _login(client)
        resp = await client.post("/admin/viajes/1/check-in/scan", json={"codigoQr": "QR-NO-EXISTE"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
