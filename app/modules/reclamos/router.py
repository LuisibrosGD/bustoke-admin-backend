from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.reclamos import service
from app.modules.reclamos.schemas import (
    MensajeReclamoCreate,
    MensajeReclamoOut,
    ReclamoCreate,
    ReclamoOut,
    ReclamoUpdate,
)

router = APIRouter(prefix="/admin/reclamos", tags=["Reclamos"])


@router.get("/", response_model=list[ReclamoOut])
async def list_reclamos(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = Query(None),
):
    return await service.get_all(db, skip, limit, id_agencia)


@router.get("/{id_reclamo}", response_model=ReclamoOut)
async def get_reclamo(id_reclamo: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_reclamo)


@router.post("/", response_model=ReclamoOut, status_code=201)
async def create_reclamo(body: ReclamoCreate, db: DbDep, _: AdminOrSuper):
    return await service.create(db, body)


@router.put("/{id_reclamo}", response_model=ReclamoOut)
async def update_reclamo(id_reclamo: int, body: ReclamoUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_reclamo(db, id_reclamo, body)


@router.delete("/{id_reclamo}")
async def delete_reclamo(id_reclamo: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_reclamo(db, id_reclamo)


# ── Mensajes ──────────────────────────────────────────────────────────────────

@router.get("/{id_reclamo}/mensajes", response_model=list[MensajeReclamoOut])
async def list_mensajes(id_reclamo: int, db: DbDep, _: AdminOrSuper):
    return await service.get_mensajes_by_reclamo(db, id_reclamo)


@router.post("/{id_reclamo}/mensajes", response_model=MensajeReclamoOut, status_code=201)
async def create_mensaje(id_reclamo: int, body: MensajeReclamoCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_mensaje(db, body)
