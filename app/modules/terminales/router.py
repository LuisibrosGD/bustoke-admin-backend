from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.terminales import service
from app.modules.terminales.schemas import TerminalCreate, TerminalOut, TerminalUpdate

router = APIRouter(prefix="/admin/terminales", tags=["Terminales"])


@router.get("/", response_model=list[TerminalOut])
async def list_terminales(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    id_agencia: int | None = Query(default=None),
):
    user_agencia = current_user.get("id_agencia")
    user_rol = current_user.get("rol")
    if id_agencia is None:
        id_agencia = user_agencia if user_rol == "admin_agencia" else None
    return await service.get_all(db, skip, limit, id_agencia=id_agencia)


@router.get("/{id_terminal}", response_model=TerminalOut)
async def get_terminal(id_terminal: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_terminal)


@router.post("/", response_model=TerminalOut, status_code=201)
async def create_terminal(
    body: TerminalCreate, db: DbDep, current_user: AdminOrSuper
):
    terminal = await service.create(db, body)
    user_agencia = current_user.get("id_agencia")
    user_rol = current_user.get("rol")
    if user_rol == "admin_agencia" and user_agencia:
        at = AgenciaTerminal(
            id_agencia=user_agencia,
            id_terminal=terminal.id_terminal,
            nro_counter_oficina="Principal",
        )
        db.add(at)
        await db.commit()
        await db.refresh(terminal)
    return terminal


@router.put("/{id_terminal}", response_model=TerminalOut)
async def update_terminal(id_terminal: int, body: TerminalUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_terminal(db, id_terminal, body)


@router.delete("/{id_terminal}")
async def delete_terminal(id_terminal: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_terminal(db, id_terminal)
