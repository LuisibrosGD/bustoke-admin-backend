from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.soporte.models import HistorialCambioSoporte, TicketSoporte
from app.modules.soporte.schemas import TicketSoporteCreate, TicketSoporteUpdate


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100, id_agencia: int | None = None) -> list[TicketSoporte]:
    stmt = select(TicketSoporte)
    if id_agencia is not None:
        stmt = stmt.where(TicketSoporte.id_agencia == id_agencia)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_ticket: int) -> TicketSoporte:
    result = await db.execute(
        select(TicketSoporte).where(TicketSoporte.id_ticket_soporte == id_ticket)
    )
    t = result.scalar_one_or_none()
    if not t:
        raise NotFoundException(f"Ticket {id_ticket} no encontrado")
    return t


async def create(db: AsyncSession, data: TicketSoporteCreate) -> TicketSoporte:
    t = TicketSoporte(
        id_agencia=data.id_agencia,
        asunto=data.asunto,
        descripcion=data.descripcion,
        estado=data.estado,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


async def update_ticket(
    db: AsyncSession, id_ticket: int, data: TicketSoporteUpdate, id_usuario_modifica: int | None = None
) -> TicketSoporte:
    t = await get_by_id(db, id_ticket)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        old_value = getattr(t, key, None)
        if key == "estado" and value != old_value:
            historial = HistorialCambioSoporte(
                id_ticket=id_ticket,
                campo="estado",
                valor_anterior=str(old_value) if old_value else None,
                valor_nuevo=str(value),
                id_usuario_modifica=id_usuario_modifica,
            )
            db.add(historial)
        setattr(t, key, value)
    await db.commit()
    await db.refresh(t)
    return t


async def get_historial(db: AsyncSession, id_ticket: int) -> list[HistorialCambioSoporte]:
    result = await db.execute(
        select(HistorialCambioSoporte)
        .where(HistorialCambioSoporte.id_ticket == id_ticket)
        .order_by(HistorialCambioSoporte.fecha_cambio.desc())
    )
    return list(result.scalars().all())


async def delete_ticket(db: AsyncSession, id_ticket: int) -> dict:
    t = await get_by_id(db, id_ticket)
    # El historial es solo el audit-trail de cambios de este ticket, sin
    # valor propio fuera de él: se elimina junto con él.
    await db.execute(delete(HistorialCambioSoporte).where(HistorialCambioSoporte.id_ticket == id_ticket))
    await db.delete(t)
    await db.commit()
    return {"message": f"Ticket {id_ticket} eliminado"}
