from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.soporte import service
from app.modules.soporte.schemas import (
    HistorialCambioOut,
    TicketSoporteCreate,
    TicketSoporteOut,
    TicketSoporteUpdate,
)

router = APIRouter(prefix="/admin/soporte", tags=["Soporte"])


@router.get("/", response_model=list[TicketSoporteOut])
async def list_tickets(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = Query(None),
):
    return await service.get_all(db, skip, limit, id_agencia)


@router.get("/{id_ticket}", response_model=TicketSoporteOut)
async def get_ticket(id_ticket: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_ticket)


@router.get("/{id_ticket}/historial", response_model=list[HistorialCambioOut])
async def get_historial(id_ticket: int, db: DbDep, _: AdminOrSuper):
    return await service.get_historial(db, id_ticket)


@router.post("/", response_model=TicketSoporteOut, status_code=201)
async def create_ticket(body: TicketSoporteCreate, db: DbDep, _: AdminOrSuper):
    return await service.create(db, body)


@router.put("/{id_ticket}", response_model=TicketSoporteOut)
async def update_ticket(
    id_ticket: int, body: TicketSoporteUpdate, db: DbDep, usuario: AdminOrSuper
):
    return await service.update_ticket(db, id_ticket, body, id_usuario_modifica=int(usuario["sub"]))


@router.delete("/{id_ticket}")
async def delete_ticket(id_ticket: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_ticket(db, id_ticket)
