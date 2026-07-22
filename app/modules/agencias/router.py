from fastapi import APIRouter, Query

from app.core.exceptions import NotFoundException
from app.dependencies import AdminOrSuper, DbDep, SuperAdmin, resolve_agencia_scope
from app.modules.agencias import service
from app.modules.agencias.schemas import AgenciaCreate, AgenciaOut, AgenciaUpdate

router = APIRouter(prefix="/admin/agencias", tags=["Agencias"])


@router.get("/", response_model=list[AgenciaOut])
async def list_agencias(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    id_agencia = resolve_agencia_scope(current_user)
    if id_agencia:
        agencia = await service.get_by_id(db, id_agencia)
        return [agencia]
    return await service.get_all(db, skip, limit)


@router.get("/{id_agencia}", response_model=AgenciaOut)
async def get_agencia(id_agencia: int, db: DbDep, current_user: AdminOrSuper):
    # admin_agencia / admin_terminal solo pueden ver su propia agencia:
    # sin este chequeo, cualquiera podia pedir el RUC/datos bancarios de
    # otra agencia con solo cambiar el id en la URL.
    scoped_id = resolve_agencia_scope(current_user, id_agencia)
    if scoped_id is not None and scoped_id != id_agencia:
        raise NotFoundException(f"Agencia {id_agencia} no encontrada")
    return await service.get_by_id(db, id_agencia)


@router.post("/", response_model=AgenciaOut, status_code=201)
async def create_agencia(body: AgenciaCreate, db: DbDep, _: SuperAdmin):
    return await service.create(db, body)


@router.put("/{id_agencia}", response_model=AgenciaOut)
async def update_agencia(id_agencia: int, body: AgenciaUpdate, db: DbDep, _: SuperAdmin):
    return await service.update_agencia(db, id_agencia, body)


@router.delete("/{id_agencia}")
async def delete_agencia(id_agencia: int, db: DbDep, _: SuperAdmin):
    return await service.delete_agencia(db, id_agencia)
