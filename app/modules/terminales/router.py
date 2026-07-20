from fastapi import APIRouter, Query

from app.core.exceptions import ForbiddenException
from app.dependencies import (
    AdminOrSuper,
    AdminOrSuperOrTerminal,
    DbDep,
    resolve_agencia_scope,
    resolve_terminal_scope,
)
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.terminales import service
from app.modules.terminales.schemas import TerminalCreate, TerminalOut, TerminalUpdate

router = APIRouter(prefix="/admin/terminales", tags=["Terminales"])


@router.get("/", response_model=list[TerminalOut])
async def list_terminales(
    db: DbDep,
    current_user: AdminOrSuperOrTerminal,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    id_agencia: int | None = Query(default=None),
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_all(db, skip, limit, id_agencia=id_agencia, id_terminal=id_terminal)


@router.get("/{id_terminal}", response_model=TerminalOut)
async def get_terminal(id_terminal: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    scoped_terminal = resolve_terminal_scope(current_user)
    if scoped_terminal and scoped_terminal != id_terminal:
        raise ForbiddenException("No tienes acceso a este terminal")
    return await service.get_by_id(db, id_terminal)


@router.post("/", response_model=TerminalOut, status_code=201)
async def create_terminal(
    body: TerminalCreate, db: DbDep, current_user: AdminOrSuper
):
    terminal = await service.create(db, body)
    id_agencia = resolve_agencia_scope(current_user)
    if id_agencia:
        at = AgenciaTerminal(
            id_agencia=id_agencia,
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
