from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.agencias_terminales.schemas import AgenciaTerminalCreate


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[AgenciaTerminal]:
    result = await db.execute(select(AgenciaTerminal).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_agencia_terminal: int) -> AgenciaTerminal:
    result = await db.execute(
        select(AgenciaTerminal).where(AgenciaTerminal.id_agencia_terminal == id_agencia_terminal)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise NotFoundException(f"AgenciaTerminal {id_agencia_terminal} no encontrada")
    return obj


async def get_by_agencia(db: AsyncSession, id_agencia: int) -> list[AgenciaTerminal]:
    result = await db.execute(
        select(AgenciaTerminal).where(AgenciaTerminal.id_agencia == id_agencia)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: AgenciaTerminalCreate) -> AgenciaTerminal:
    obj = AgenciaTerminal(
        id_agencia=data.id_agencia,
        id_terminal=data.id_terminal,
        nro_counter_oficina=data.nro_counter_oficina,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, id_agencia_terminal: int) -> dict:
    obj = await get_by_id(db, id_agencia_terminal)
    await db.delete(obj)
    await db.commit()
    return {"message": f"AgenciaTerminal {id_agencia_terminal} eliminada"}
