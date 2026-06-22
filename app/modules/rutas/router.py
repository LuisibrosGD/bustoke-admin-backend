from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.rutas import service
from app.modules.rutas.schemas import (
    RutaCreate,
    RutaOut,
    RutaUpdate,
    TarifaRutaCreate,
    TarifaRutaOut,
    TarifaRutaUpdate,
)

router = APIRouter(prefix="/admin/rutas", tags=["Rutas"])


# ── Rutas ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[RutaOut])
async def list_rutas(
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
        return await service.get_rutas_by_agencia(db, id_agencia)
    return await service.get_all_rutas(db, skip, limit)


@router.get("/{id_ruta}", response_model=RutaOut)
async def get_ruta(id_ruta: int, db: DbDep, _: AdminOrSuper):
    return await service.get_ruta_by_id(db, id_ruta)


@router.post("/", response_model=RutaOut, status_code=201)
async def create_ruta(body: RutaCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_ruta(db, body)


@router.put("/{id_ruta}", response_model=RutaOut)
async def update_ruta(id_ruta: int, body: RutaUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_ruta(db, id_ruta, body)


@router.delete("/{id_ruta}")
async def delete_ruta(id_ruta: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_ruta(db, id_ruta)


# ── Tarifas ───────────────────────────────────────────────────────────────────

@router.get("/{id_ruta}/tarifas", response_model=list[TarifaRutaOut])
async def list_tarifas(id_ruta: int, db: DbDep, _: AdminOrSuper):
    return await service.get_tarifas_by_ruta(db, id_ruta)


@router.get("/tarifas/{id_tarifa}", response_model=TarifaRutaOut)
async def get_tarifa(id_tarifa: int, db: DbDep, _: AdminOrSuper):
    return await service.get_tarifa_by_id(db, id_tarifa)


@router.post("/tarifas", response_model=TarifaRutaOut, status_code=201)
async def create_tarifa(body: TarifaRutaCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_tarifa(db, body)


@router.put("/tarifas/{id_tarifa}", response_model=TarifaRutaOut)
async def update_tarifa(id_tarifa: int, body: TarifaRutaUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_tarifa(db, id_tarifa, body)


@router.delete("/tarifas/{id_tarifa}")
async def delete_tarifa(id_tarifa: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_tarifa(db, id_tarifa)
