from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.choferes.models import Chofer
from app.modules.choferes.schemas import ChoferCreate, ChoferUpdate


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Chofer]:
    result = await db.execute(select(Chofer).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_chofer: int) -> Chofer:
    result = await db.execute(select(Chofer).where(Chofer.id_chofer == id_chofer))
    chofer = result.scalar_one_or_none()
    if not chofer:
        raise NotFoundException(f"Chofer {id_chofer} no encontrado")
    return chofer


async def get_by_agencia(db: AsyncSession, id_agencia: int) -> list[Chofer]:
    result = await db.execute(select(Chofer).where(Chofer.id_agencia == id_agencia))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: ChoferCreate) -> Chofer:
    existing = await db.execute(
        select(Chofer).where(Chofer.numero_documento == data.numero_documento)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(
            f"Ya existe un chofer con documento {data.numero_documento}"
        )
    chofer = Chofer(
        id_agencia=data.id_agencia,
        id_tipo_documento=data.id_tipo_documento,
        numero_documento=data.numero_documento,
        nombres=data.nombres,
        apellido_paterno=data.apellido_paterno,
        apellido_materno=data.apellido_materno,
        activo=data.activo,
    )
    db.add(chofer)
    await db.commit()
    await db.refresh(chofer)
    return chofer


async def update(db: AsyncSession, id_chofer: int, data: ChoferUpdate) -> Chofer:
    chofer = await get_by_id(db, id_chofer)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(chofer, key, value)
    await db.commit()
    await db.refresh(chofer)
    return chofer


async def delete(db: AsyncSession, id_chofer: int) -> dict:
    chofer = await get_by_id(db, id_chofer)
    await db.delete(chofer)
    await db.commit()
    return {"message": f"Chofer {id_chofer} eliminado"}
