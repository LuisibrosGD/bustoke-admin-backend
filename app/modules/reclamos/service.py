from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.notificaciones.models import Notificacion
from app.modules.reclamos.models import MensajeReclamo, Reclamo
from app.modules.reclamos.schemas import (
    MensajeReclamoCreate,
    ReclamoCreate,
    ReclamoUpdate,
)


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100, id_agencia: int | None = None) -> list[Reclamo]:
    stmt = select(Reclamo)
    if id_agencia is not None:
        stmt = stmt.where(Reclamo.id_agencia == id_agencia)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_reclamo: int) -> Reclamo:
    result = await db.execute(select(Reclamo).where(Reclamo.id_reclamo == id_reclamo))
    r = result.scalar_one_or_none()
    if not r:
        raise NotFoundException(f"Reclamo {id_reclamo} no encontrado")
    return r


async def create(db: AsyncSession, data: ReclamoCreate) -> Reclamo:
    r = Reclamo(
        id_usuario=data.id_usuario,
        id_agencia=data.id_agencia,
        motivo=data.motivo,
        detalle=data.detalle,
        estado=data.estado,
    )
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


async def update_reclamo(db: AsyncSession, id_reclamo: int, data: ReclamoUpdate) -> Reclamo:
    r = await get_by_id(db, id_reclamo)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(r, key, value)
    await db.commit()
    await db.refresh(r)
    return r


async def delete_reclamo(db: AsyncSession, id_reclamo: int) -> dict:
    r = await get_by_id(db, id_reclamo)
    # Los mensajes son solo el hilo de conversación de este reclamo, sin
    # valor propio fuera de él: se eliminan junto con él.
    await db.execute(delete(MensajeReclamo).where(MensajeReclamo.id_reclamo == id_reclamo))
    await db.delete(r)
    await db.commit()
    return {"message": f"Reclamo {id_reclamo} eliminado"}


async def get_mensajes_by_reclamo(db: AsyncSession, id_reclamo: int) -> list[MensajeReclamo]:
    result = await db.execute(
        select(MensajeReclamo)
        .where(MensajeReclamo.id_reclamo == id_reclamo)
        .order_by(MensajeReclamo.fecha)
    )
    return list(result.scalars().all())


async def create_mensaje(db: AsyncSession, data: MensajeReclamoCreate) -> MensajeReclamo:
    reclamo = await get_by_id(db, data.id_reclamo)
    m = MensajeReclamo(
        id_reclamo=data.id_reclamo,
        id_usuario=data.id_usuario,
        text_mensaje=data.text_mensaje,
    )
    db.add(m)

    if data.id_usuario != reclamo.id_usuario:
        titulo = f"Nuevo mensaje en reclamo: {reclamo.motivo}"[:150]
        n = Notificacion(
            id_usuario=reclamo.id_usuario,
            tipo="mensaje_reclamo",
            titulo=titulo,
            mensaje=data.text_mensaje[:200],
            referencia_tipo="reclamo",
            referencia_id=reclamo.id_reclamo,
        )
        db.add(n)

    await db.commit()
    await db.refresh(m)
    return m
