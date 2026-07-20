from fastapi import APIRouter, Query

from app.dependencies import (
    AdminOrSuper,
    AdminOrSuperOrTerminal,
    DbDep,
    resolve_agencia_scope,
    resolve_terminal_scope,
)
from app.modules.viajes import service
from app.modules.viajes.schemas import (
    BoletoCheckIn,
    BoletoCreate,
    BoletoOut,
    BoletoScanRequest,
    BoletoUpdate,
    PasajeroCreate,
    PasajeroOut,
    PasajeroUpdate,
    ViajeCreate,
    ViajeOut,
    ViajeUpdate,
)

router = APIRouter(prefix="/admin/viajes", tags=["Viajes"])


# ── Viajes ────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ViajeOut])
async def list_viajes(
    db: DbDep,
    current_user: AdminOrSuperOrTerminal,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
    id_bus: int | None = None,
    id_ruta: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    id_terminal = resolve_terminal_scope(current_user)
    if id_bus is not None:
        return await service.get_viajes_by_bus(db, id_bus, skip, limit, id_agencia)
    if id_ruta is not None:
        return await service.get_viajes_by_ruta(db, id_ruta, skip, limit, id_agencia)
    if id_agencia or id_terminal:
        return await service.get_viajes_scoped(db, skip, limit, id_agencia, id_terminal)
    return await service.get_all_viajes(db, skip, limit)


@router.get("/{id_viaje}", response_model=ViajeOut)
async def get_viaje(id_viaje: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_viaje_by_id(db, id_viaje, id_agencia, id_terminal)


@router.post("/", response_model=ViajeOut, status_code=201)
async def create_viaje(body: ViajeCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_viaje(db, body)


@router.put("/{id_viaje}", response_model=ViajeOut)
async def update_viaje(id_viaje: int, body: ViajeUpdate, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await service.update_viaje(db, id_viaje, body, id_agencia)


@router.delete("/{id_viaje}")
async def delete_viaje(id_viaje: int, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await service.delete_viaje(db, id_viaje, id_agencia)


# ── Boletos ───────────────────────────────────────────────────────────────────

@router.get("/{id_viaje}/boletos", response_model=list[BoletoOut])
async def list_boletos_by_viaje(id_viaje: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_boletos_by_viaje(db, id_viaje, id_agencia, id_terminal)


@router.get("/boletos/all", response_model=list[BoletoOut])
async def list_all_boletos(
    db: DbDep,
    current_user: AdminOrSuperOrTerminal,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    if id_agencia:
        return await service.get_boletos_by_agencia(db, id_agencia, skip, limit, id_terminal)
    return await service.get_all_boletos(db, skip, limit)


@router.get("/boletos/{id_boleto}", response_model=BoletoOut)
async def get_boleto(id_boleto: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_boleto_by_id(db, id_boleto, id_agencia, id_terminal)


@router.post("/boletos", response_model=BoletoOut, status_code=201)
async def create_boleto(body: BoletoCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_boleto(db, body)


@router.put("/boletos/{id_boleto}", response_model=BoletoOut)
async def update_boleto(id_boleto: int, body: BoletoUpdate, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.update_boleto(db, id_boleto, body, id_agencia, id_terminal)


@router.delete("/boletos/{id_boleto}")
async def delete_boleto(id_boleto: int, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await service.delete_boleto(db, id_boleto, id_agencia)


@router.put("/boletos/{id_boleto}/check-in", response_model=BoletoOut)
async def checkin_boleto(id_boleto: int, body: BoletoCheckIn, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.update_boleto_checkin(db, id_boleto, body.estado_checkin, id_agencia, id_terminal)


@router.post("/{id_viaje}/check-in/scan", response_model=BoletoOut)
async def scan_qr_checkin(id_viaje: int, body: BoletoScanRequest, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.scan_boleto_by_qr(db, id_viaje, body.codigo_qr, id_agencia, id_terminal)


# ── Pasajeros ─────────────────────────────────────────────────────────────────

@router.get("/{id_viaje}/pasajeros", response_model=list[PasajeroOut])
async def list_pasajeros_by_viaje(id_viaje: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_pasajeros_by_viaje(db, id_viaje, id_agencia, id_terminal)


@router.get("/pasajeros/all", response_model=list[PasajeroOut])
async def list_pasajeros(
    db: DbDep,
    current_user: AdminOrSuperOrTerminal,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    if id_agencia:
        return await service.get_pasajeros_by_agencia(db, id_agencia, skip, limit, id_terminal)
    return await service.get_all_pasajeros(db, skip, limit)


@router.get("/pasajeros/{id_pasajero}", response_model=PasajeroOut)
async def get_pasajero(id_pasajero: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_pasajero_by_id(db, id_pasajero, id_agencia, id_terminal)


@router.post("/pasajeros", response_model=PasajeroOut, status_code=201)
async def create_pasajero(body: PasajeroCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_pasajero(db, body)


@router.put("/pasajeros/{id_pasajero}", response_model=PasajeroOut)
async def update_pasajero(id_pasajero: int, body: PasajeroUpdate, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.update_pasajero(db, id_pasajero, body, id_agencia, id_terminal)


@router.delete("/pasajeros/{id_pasajero}")
async def delete_pasajero(id_pasajero: int, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await service.delete_pasajero(db, id_pasajero, id_agencia)
