from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ubigeo.models import Departamento, Distrito, Provincia


async def get_departamentos(db: AsyncSession) -> list[Departamento]:
    result = await db.execute(select(Departamento).order_by(Departamento.nombre))
    return list(result.scalars().all())


async def get_provincias(db: AsyncSession, id_departamento: int | None = None) -> list[Provincia]:
    q = select(Provincia)
    if id_departamento:
        q = q.where(Provincia.id_departamento == id_departamento)
    result = await db.execute(q.order_by(Provincia.nombre))
    return list(result.scalars().all())


async def get_distritos(db: AsyncSession, id_provincia: int | None = None) -> list[Distrito]:
    q = select(Distrito)
    if id_provincia:
        q = q.where(Distrito.id_provincia == id_provincia)
    result = await db.execute(q.order_by(Distrito.nombre))
    return list(result.scalars().all())
