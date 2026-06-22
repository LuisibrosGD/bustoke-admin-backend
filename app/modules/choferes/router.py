from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.choferes import service
from app.modules.choferes.schemas import (
    ChoferCreate,
    ChoferOut,
    ChoferUpdate,
)

router = APIRouter(prefix="/admin/choferes", tags=["Choferes"])


@router.get("/", response_model=list[ChoferOut])
async def list_choferes(
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
        return await service.get_by_agencia(db, id_agencia)
    return await service.get_all(db, skip, limit)


@router.get("/{id_chofer}", response_model=ChoferOut)
async def get_chofer(id_chofer: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_chofer)


@router.post("/", response_model=ChoferOut, status_code=201)
async def create_chofer(body: ChoferCreate, db: DbDep, _: AdminOrSuper):
    return await service.create(db, body)


@router.put("/{id_chofer}", response_model=ChoferOut)
async def update_chofer(id_chofer: int, body: ChoferUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update(db, id_chofer, body)


@router.delete("/{id_chofer}")
async def delete_chofer(id_chofer: int, db: DbDep, _: AdminOrSuper):
    return await service.delete(db, id_chofer)
