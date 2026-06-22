from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.notificaciones.models import Notificacion
from app.modules.notificaciones.schemas import NotificacionUpdate


async def get_notificaciones_by_usuario(
    db: AsyncSession, id_usuario: int, solo_no_leidas: bool = False
) -> list[Notificacion]:
    query = select(Notificacion).where(
        Notificacion.id_usuario == id_usuario
    ).order_by(Notificacion.fecha_creacion.desc())
    if solo_no_leidas:
        query = query.where(Notificacion.leida == False)
    result = await db.execute(query)
    return list(result.scalars().all())


async def crear_notificacion(
    db: AsyncSession,
    id_usuario: int,
    tipo: str,
    titulo: str,
    mensaje: str,
    referencia_tipo: str | None = None,
    referencia_id: int | None = None,
) -> Notificacion:
    n = Notificacion(
        id_usuario=id_usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        referencia_tipo=referencia_tipo,
        referencia_id=referencia_id,
    )
    db.add(n)
    await db.commit()
    await db.refresh(n)
    return n


async def marcar_como_leida(
    db: AsyncSession, id_notificacion: int, id_usuario: int
) -> Notificacion:
    result = await db.execute(
        select(Notificacion).where(
            Notificacion.id_notificacion == id_notificacion,
            Notificacion.id_usuario == id_usuario,
        )
    )
    n = result.scalar_one_or_none()
    if not n:
        raise NotFoundException("Notificacion no encontrada")
    n.leida = True
    await db.commit()
    await db.refresh(n)
    return n


async def marcar_todas_leidas(db: AsyncSession, id_usuario: int) -> int:
    result = await db.execute(
        select(Notificacion).where(
            Notificacion.id_usuario == id_usuario,
            Notificacion.leida == False,
        )
    )
    notificaciones = list(result.scalars().all())
    for n in notificaciones:
        n.leida = True
    await db.commit()
    return len(notificaciones)


async def contar_no_leidas(db: AsyncSession, id_usuario: int) -> int:
    result = await db.execute(
        select(Notificacion).where(
            Notificacion.id_usuario == id_usuario,
            Notificacion.leida == False,
        )
    )
    return len(list(result.scalars().all()))
