from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.viajes import service
from app.modules.viajes.schemas import (
    BoletoCreate,
    BoletoOut,
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
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
    id_bus: int | None = None,
):
    if id_bus is not None:
        return await service.get_viajes_by_bus(db, id_bus, skip, limit)
    user_agencia = current_user.get("id_agencia")
    user_rol = current_user.get("rol")
    if user_rol == "admin_agencia" and user_agencia:
        id_agencia = user_agencia
    if id_agencia:
        return await service.get_viajes_by_agencia(db, id_agencia, skip, limit)
    return await service.get_all_viajes(db, skip, limit)


@router.get("/{id_viaje}", response_model=ViajeOut)
async def get_viaje(id_viaje: int, db: DbDep, _: AdminOrSuper):
    return await service.get_viaje_by_id(db, id_viaje)


@router.post("/", response_model=ViajeOut, status_code=201)
async def create_viaje(body: ViajeCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_viaje(db, body)


@router.put("/{id_viaje}", response_model=ViajeOut)
async def update_viaje(id_viaje: int, body: ViajeUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_viaje(db, id_viaje, body)


@router.delete("/{id_viaje}")
async def delete_viaje(id_viaje: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_viaje(db, id_viaje)


# ── Boletos ───────────────────────────────────────────────────────────────────

@router.get("/{id_viaje}/boletos", response_model=list[BoletoOut])
async def list_boletos_by_viaje(id_viaje: int, db: DbDep, _: AdminOrSuper):
    return await service.get_boletos_by_viaje(db, id_viaje)


@router.get("/boletos/all", response_model=list[BoletoOut])
async def list_all_boletos(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await service.get_all_boletos(db, skip, limit)


@router.get("/boletos/{id_boleto}", response_model=BoletoOut)
async def get_boleto(id_boleto: int, db: DbDep, _: AdminOrSuper):
    return await service.get_boleto_by_id(db, id_boleto)


@router.post("/boletos", response_model=BoletoOut, status_code=201)
async def create_boleto(body: BoletoCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_boleto(db, body)


@router.put("/boletos/{id_boleto}", response_model=BoletoOut)
async def update_boleto(id_boleto: int, body: BoletoUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_boleto(db, id_boleto, body)


@router.delete("/boletos/{id_boleto}")
async def delete_boleto(id_boleto: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_boleto(db, id_boleto)


# ── Pasajeros ─────────────────────────────────────────────────────────────────

@router.get("/{id_viaje}/pasajeros", response_model=list[PasajeroOut])
async def list_pasajeros_by_viaje(id_viaje: int, db: DbDep, _: AdminOrSuper):
    return await service.get_pasajeros_by_viaje(db, id_viaje)


@router.get("/pasajeros/all", response_model=list[PasajeroOut])
async def list_pasajeros(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await service.get_all_pasajeros(db, skip, limit)


@router.get("/pasajeros/{id_pasajero}", response_model=PasajeroOut)
async def get_pasajero(id_pasajero: int, db: DbDep, _: AdminOrSuper):
    return await service.get_pasajero_by_id(db, id_pasajero)


@router.post("/pasajeros", response_model=PasajeroOut, status_code=201)
async def create_pasajero(body: PasajeroCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_pasajero(db, body)


@router.put("/pasajeros/{id_pasajero}", response_model=PasajeroOut)
async def update_pasajero(id_pasajero: int, body: PasajeroUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_pasajero(db, id_pasajero, body)


@router.delete("/pasajeros/{id_pasajero}")
async def delete_pasajero(id_pasajero: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_pasajero(db, id_pasajero)
