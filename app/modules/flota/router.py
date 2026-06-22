from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.flota import service
from app.modules.flota.schemas import (
    AsientoCreate,
    AsientoOut,
    AsientoUpdate,
    BusCreate,
    BusOut,
    BusUpdate,
)

router = APIRouter(prefix="/admin/flota", tags=["Flota"])


# ── Buses ─────────────────────────────────────────────────────────────────────

@router.get("/buses", response_model=list[BusOut])
async def list_buses(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    user_agencia = current_user.get("id_agencia")
    user_rol = current_user.get("rol")
    if user_rol == "admin_agencia" and user_agencia:
        id_agencia = user_agencia
    if id_agencia:
        return await service.get_buses_by_agencia(db, id_agencia)
    return await service.get_all_buses(db, skip, limit)


@router.get("/buses/{id_bus}", response_model=BusOut)
async def get_bus(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.get_bus_by_id(db, id_bus)


@router.post("/buses", response_model=BusOut, status_code=201)
async def create_bus(body: BusCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_bus(db, body)


@router.put("/buses/{id_bus}", response_model=BusOut)
async def update_bus(id_bus: int, body: BusUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_bus(db, id_bus, body)


@router.delete("/buses/{id_bus}")
async def delete_bus(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_bus(db, id_bus)


# ── Asientos ──────────────────────────────────────────────────────────────────

@router.get("/buses/{id_bus}/asientos", response_model=list[AsientoOut])
async def list_asientos(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.get_asientos_by_bus(db, id_bus)


@router.get("/asientos/{id_asiento}", response_model=AsientoOut)
async def get_asiento(id_asiento: int, db: DbDep, _: AdminOrSuper):
    return await service.get_asiento_by_id(db, id_asiento)


@router.post("/asientos", response_model=AsientoOut, status_code=201)
async def create_asiento(body: AsientoCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_asiento(db, body)


@router.put("/asientos/{id_asiento}", response_model=AsientoOut)
async def update_asiento(id_asiento: int, body: AsientoUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_asiento(db, id_asiento, body)


@router.delete("/asientos/{id_asiento}")
async def delete_asiento(id_asiento: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_asiento(db, id_asiento)
