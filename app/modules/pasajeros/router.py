from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep, resolve_agencia_scope
from app.modules.viajes import service as viajes_service
from app.modules.viajes.schemas import PasajeroCreate, PasajeroOut, PasajeroUpdate

router = APIRouter(prefix="/admin/pasajeros", tags=["Pasajeros"])


@router.get("/", response_model=list[PasajeroOut])
async def list_pasajeros(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    if id_agencia:
        return await viajes_service.get_pasajeros_by_agencia(db, id_agencia, skip, limit)
    return await viajes_service.get_all_pasajeros(db, skip, limit)


@router.get("/{id_pasajero}", response_model=PasajeroOut)
async def get_pasajero(id_pasajero: int, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await viajes_service.get_pasajero_by_id(db, id_pasajero, id_agencia)


@router.post("/", response_model=PasajeroOut, status_code=201)
async def create_pasajero(body: PasajeroCreate, db: DbDep, _: AdminOrSuper):
    return await viajes_service.create_pasajero(db, body)


@router.put("/{id_pasajero}", response_model=PasajeroOut)
async def update_pasajero(id_pasajero: int, body: PasajeroUpdate, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await viajes_service.update_pasajero(db, id_pasajero, body, id_agencia)


@router.delete("/{id_pasajero}")
async def delete_pasajero(id_pasajero: int, db: DbDep, current_user: AdminOrSuper):
    id_agencia = resolve_agencia_scope(current_user)
    return await viajes_service.delete_pasajero(db, id_pasajero, id_agencia)
