from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundException
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.terminales.models import Terminal
from app.modules.terminales.schemas import TerminalCreate, TerminalUpdate


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 200,
    id_agencia: int | None = None,
    id_terminal: int | None = None,
) -> list[Terminal]:
    query = select(Terminal)
    if id_agencia is not None:
        query = (
            select(Terminal)
            .join(AgenciaTerminal, AgenciaTerminal.id_terminal == Terminal.id_terminal)
            .where(AgenciaTerminal.id_agencia == id_agencia)
        )
    if id_terminal is not None:
        query = query.where(Terminal.id_terminal == id_terminal)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_terminal: int) -> Terminal:
    result = await db.execute(select(Terminal).where(Terminal.id_terminal == id_terminal))
    terminal = result.scalar_one_or_none()
    if not terminal:
        raise NotFoundException(f"Terminal {id_terminal} no encontrado")
    return terminal


async def create(db: AsyncSession, data: TerminalCreate) -> Terminal:
    terminal = Terminal(
        id_distrito=data.id_distrito,
        nombre=data.nombre,
        direccion=data.direccion,
    )
    db.add(terminal)
    await db.commit()
    await db.refresh(terminal)
    return terminal


async def update_terminal(db: AsyncSession, id_terminal: int, data: TerminalUpdate) -> Terminal:
    terminal = await get_by_id(db, id_terminal)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(terminal, key, value)
    await db.commit()
    await db.refresh(terminal)
    return terminal


async def delete_terminal(db: AsyncSession, id_terminal: int) -> dict:
    terminal = await get_by_id(db, id_terminal)
    await db.delete(terminal)
    await db.commit()
    return {"message": f"Terminal {id_terminal} eliminado"}
