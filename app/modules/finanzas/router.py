from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep, SuperAdmin
from app.modules.finanzas import service
from app.modules.finanzas.schemas import (
    ApiKeyCreate,
    ApiKeyOut,
    ApiKeyUpdate,
    LiquidacionCreate,
    LiquidacionOut,
    LiquidacionUpdate,
)

router = APIRouter(tags=["Finanzas"])


# ── Liquidaciones ─────────────────────────────────────────────────────────────

@router.get("/admin/liquidaciones", response_model=list[LiquidacionOut])
async def list_liquidaciones(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    if id_agencia:
        return await service.get_liquidaciones_by_agencia(db, id_agencia)
    return await service.get_all_liquidaciones(db, skip, limit)


@router.get("/admin/liquidaciones/{id_liquidacion}", response_model=LiquidacionOut)
async def get_liquidacion(id_liquidacion: int, db: DbDep, _: AdminOrSuper):
    return await service.get_liquidacion_by_id(db, id_liquidacion)


@router.post("/admin/liquidaciones", response_model=LiquidacionOut, status_code=201)
async def create_liquidacion(body: LiquidacionCreate, db: DbDep, _: SuperAdmin):
    return await service.create_liquidacion(db, body)


@router.put("/admin/liquidaciones/{id_liquidacion}", response_model=LiquidacionOut)
async def update_liquidacion(
    id_liquidacion: int, body: LiquidacionUpdate, db: DbDep, _: SuperAdmin
):
    return await service.update_liquidacion(db, id_liquidacion, body)


@router.delete("/admin/liquidaciones/{id_liquidacion}")
async def delete_liquidacion(id_liquidacion: int, db: DbDep, _: SuperAdmin):
    return await service.delete_liquidacion(db, id_liquidacion)


# ── Api Keys ──────────────────────────────────────────────────────────────────

@router.get("/admin/api-keys", response_model=list[ApiKeyOut])
async def list_api_keys(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    if id_agencia:
        return await service.get_api_keys_by_agencia(db, id_agencia)
    return await service.get_all_api_keys(db, skip, limit)


@router.get("/admin/api-keys/{id_api_key}", response_model=ApiKeyOut)
async def get_api_key(id_api_key: int, db: DbDep, _: AdminOrSuper):
    return await service.get_api_key_by_id(db, id_api_key)


@router.post("/admin/api-keys", response_model=ApiKeyOut, status_code=201)
async def create_api_key(body: ApiKeyCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_api_key(db, body)


@router.put("/admin/api-keys/{id_api_key}", response_model=ApiKeyOut)
async def update_api_key(id_api_key: int, body: ApiKeyUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_api_key(db, id_api_key, body)


@router.delete("/admin/api-keys/{id_api_key}")
async def delete_api_key(id_api_key: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_api_key(db, id_api_key)
