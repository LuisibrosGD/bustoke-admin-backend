from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.agencias.models import Agencia
from app.modules.agencias.schemas import AgenciaCreate, AgenciaUpdate


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Agencia]:
    result = await db.execute(select(Agencia).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_agencia: int) -> Agencia:
    result = await db.execute(select(Agencia).where(Agencia.id_agencia == id_agencia))
    agencia = result.scalar_one_or_none()
    if not agencia:
        raise NotFoundException(f"Agencia {id_agencia} no encontrada")
    return agencia


async def create(db: AsyncSession, data: AgenciaCreate) -> Agencia:
    existing = await db.execute(select(Agencia).where(Agencia.ruc == data.ruc))
    if existing.scalar_one_or_none():
        raise ConflictException(f"Ya existe una agencia con RUC {data.ruc}")
    agencia = Agencia(
        ruc=data.ruc,
        razon_social=data.razon_social,
        estado=data.estado,
        banco_nombre=data.banco_nombre,
        numero_cuenta=data.numero_cuenta,
        cuenta_cci=data.cuenta_cci,
    )
    db.add(agencia)
    await db.commit()
    await db.refresh(agencia)
    return agencia


async def update_agencia(db: AsyncSession, id_agencia: int, data: AgenciaUpdate) -> Agencia:
    agencia = await get_by_id(db, id_agencia)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(agencia, key, value)
    await db.commit()
    await db.refresh(agencia)
    return agencia


async def delete_agencia(db: AsyncSession, id_agencia: int) -> dict:
    agencia = await get_by_id(db, id_agencia)
    await db.delete(agencia)
    await db.commit()
    return {"message": f"Agencia {id_agencia} eliminada correctamente"}
