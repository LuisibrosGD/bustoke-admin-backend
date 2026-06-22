from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.flota.models import Asiento, Bus
from app.modules.flota.schemas import AsientoCreate, AsientoUpdate, BusCreate, BusUpdate


# ── Buses ─────────────────────────────────────────────────────────────────────

async def get_all_buses(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Bus]:
    result = await db.execute(select(Bus).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_buses_by_agencia(db: AsyncSession, id_agencia: int) -> list[Bus]:
    result = await db.execute(select(Bus).where(Bus.id_agencia == id_agencia))
    return list(result.scalars().all())


async def get_bus_by_id(db: AsyncSession, id_bus: int) -> Bus:
    result = await db.execute(select(Bus).where(Bus.id_bus == id_bus))
    bus = result.scalar_one_or_none()
    if not bus:
        raise NotFoundException(f"Bus {id_bus} no encontrado")
    return bus


async def create_bus(db: AsyncSession, data: BusCreate) -> Bus:
    existing = await db.execute(select(Bus).where(Bus.placa == data.placa))
    if existing.scalar_one_or_none():
        raise ConflictException(f"Ya existe un bus con placa {data.placa}")
    bus = Bus(
        id_agencia=data.id_agencia,
        placa=data.placa,
        cantidad_pisos=data.cantidad_pisos,
    )
    db.add(bus)
    await db.commit()
    await db.refresh(bus)
    return bus


async def update_bus(db: AsyncSession, id_bus: int, data: BusUpdate) -> Bus:
    bus = await get_bus_by_id(db, id_bus)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(bus, key, value)
    await db.commit()
    await db.refresh(bus)
    return bus


async def delete_bus(db: AsyncSession, id_bus: int) -> dict:
    bus = await get_bus_by_id(db, id_bus)
    await db.delete(bus)
    await db.commit()
    return {"message": f"Bus {id_bus} eliminado"}


# ── Asientos ──────────────────────────────────────────────────────────────────

async def get_asientos_by_bus(db: AsyncSession, id_bus: int) -> list[Asiento]:
    result = await db.execute(select(Asiento).where(Asiento.id_bus == id_bus))
    return list(result.scalars().all())


async def get_asiento_by_id(db: AsyncSession, id_asiento: int) -> Asiento:
    result = await db.execute(select(Asiento).where(Asiento.id_asiento == id_asiento))
    asiento = result.scalar_one_or_none()
    if not asiento:
        raise NotFoundException(f"Asiento {id_asiento} no encontrado")
    return asiento


async def create_asiento(db: AsyncSession, data: AsientoCreate) -> Asiento:
    asiento = Asiento(
        id_bus=data.id_bus,
        numero_asiento=data.numero_asiento,
        fila=data.fila,
        piso=data.piso,
        tipo_servicio=data.tipo_servicio,
        coord_x=data.coord_x,
        coord_y=data.coord_y,
        bloqueado_manual=data.bloqueado_manual,
    )
    db.add(asiento)
    await db.commit()
    await db.refresh(asiento)
    return asiento


async def update_asiento(db: AsyncSession, id_asiento: int, data: AsientoUpdate) -> Asiento:
    asiento = await get_asiento_by_id(db, id_asiento)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(asiento, key, value)
    await db.commit()
    await db.refresh(asiento)
    return asiento


async def delete_asiento(db: AsyncSession, id_asiento: int) -> dict:
    asiento = await get_asiento_by_id(db, id_asiento)
    await db.delete(asiento)
    await db.commit()
    return {"message": f"Asiento {id_asiento} eliminado"}
