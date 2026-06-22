from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.agencias_terminales import service
from app.modules.agencias_terminales.schemas import AgenciaTerminalCreate, AgenciaTerminalOut

router = APIRouter(prefix="/admin/agencias-terminales", tags=["Agencias Terminales"])


@router.get("/", response_model=list[AgenciaTerminalOut])
async def list_all(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    if id_agencia:
        return await service.get_by_agencia(db, id_agencia)
    return await service.get_all(db, skip, limit)


@router.get("/{id_agencia_terminal}", response_model=AgenciaTerminalOut)
async def get_one(id_agencia_terminal: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_agencia_terminal)


@router.post("/", response_model=AgenciaTerminalOut, status_code=201)
async def create(body: AgenciaTerminalCreate, db: DbDep, _: AdminOrSuper):
    return await service.create(db, body)


@router.delete("/{id_agencia_terminal}")
async def delete(id_agencia_terminal: int, db: DbDep, _: AdminOrSuper):
    return await service.delete(db, id_agencia_terminal)
