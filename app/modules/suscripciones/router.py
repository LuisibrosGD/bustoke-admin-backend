from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep, SuperAdmin
from app.modules.suscripciones import service
from app.modules.suscripciones.schemas import (
    PlanCreate,
    PlanOut,
    PlanUpdate,
    SuscripcionCreate,
    SuscripcionOut,
    SuscripcionUpdate,
)

router = APIRouter(tags=["Suscripciones"])


# ── Planes ────────────────────────────────────────────────────────────────────

plan_router = APIRouter(prefix="/admin/planes", tags=["Planes"])


@plan_router.get("/", response_model=list[PlanOut])
async def list_planes(db: DbDep, _: AdminOrSuper):
    return await service.get_all_planes(db)


@plan_router.get("/{id_plan}", response_model=PlanOut)
async def get_plan(id_plan: int, db: DbDep, _: AdminOrSuper):
    return await service.get_plan_by_id(db, id_plan)


@plan_router.post("/", response_model=PlanOut, status_code=201)
async def create_plan(body: PlanCreate, db: DbDep, _: SuperAdmin):
    return await service.create_plan(db, body)


@plan_router.put("/{id_plan}", response_model=PlanOut)
async def update_plan(id_plan: int, body: PlanUpdate, db: DbDep, _: SuperAdmin):
    return await service.update_plan(db, id_plan, body)


@plan_router.delete("/{id_plan}")
async def delete_plan(id_plan: int, db: DbDep, _: SuperAdmin):
    return await service.delete_plan(db, id_plan)


# ── Suscripciones ─────────────────────────────────────────────────────────────

suscripcion_router = APIRouter(prefix="/admin/suscripciones", tags=["Suscripciones"])


@suscripcion_router.get("/", response_model=list[SuscripcionOut])
async def list_suscripciones(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    if id_agencia:
        return await service.get_by_agencia(db, id_agencia)
    return await service.get_all(db, skip, limit)


@suscripcion_router.get("/{id_suscripcion}", response_model=SuscripcionOut)
async def get_suscripcion(id_suscripcion: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_suscripcion)


@suscripcion_router.post("/", response_model=SuscripcionOut, status_code=201)
async def create_suscripcion(body: SuscripcionCreate, db: DbDep, _: SuperAdmin):
    return await service.create(db, body)


@suscripcion_router.put("/{id_suscripcion}", response_model=SuscripcionOut)
async def update_suscripcion(id_suscripcion: int, body: SuscripcionUpdate, db: DbDep, _: SuperAdmin):
    return await service.update_suscripcion(db, id_suscripcion, body)


@suscripcion_router.delete("/{id_suscripcion}")
async def delete_suscripcion(id_suscripcion: int, db: DbDep, _: SuperAdmin):
    return await service.delete_suscripcion(db, id_suscripcion)
