from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.flota.models import Bus
from app.modules.rutas.models import Ruta

from app.core.exceptions import NotFoundException
from app.modules.viajes.models import Boleto, Pasajero, Viaje
from app.modules.viajes.schemas import (
    BoletoCreate,
    BoletoUpdate,
    PasajeroCreate,
    PasajeroUpdate,
    ViajeCreate,
    ViajeUpdate,
)


# ── Viajes ────────────────────────────────────────────────────────────────────

async def get_all_viajes(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Viaje]:
    result = await db.execute(select(Viaje).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_viajes_by_bus(db: AsyncSession, id_bus: int, skip: int = 0, limit: int = 100) -> list[Viaje]:
    result = await db.execute(
        select(Viaje)
        .where(Viaje.id_bus == id_bus)
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_viajes_by_agencia(db: AsyncSession, id_agencia: int, skip: int = 0, limit: int = 100) -> list[Viaje]:
    result = await db.execute(
        select(Viaje)
        .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
        .where(Ruta.id_agencia == id_agencia)
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_viaje_by_id(db: AsyncSession, id_viaje: int) -> Viaje:
    result = await db.execute(select(Viaje).where(Viaje.id_viaje == id_viaje))
    viaje = result.scalar_one_or_none()
    if not viaje:
        raise NotFoundException(f"Viaje {id_viaje} no encontrado")
    return viaje


async def create_viaje(db: AsyncSession, data: ViajeCreate) -> Viaje:
    viaje = Viaje(
        id_ruta=data.id_ruta,
        id_bus=data.id_bus,
        id_chofer=data.id_chofer,
        fecha_hora_salida=data.fecha_hora_salida,
        fecha_hora_llegada=data.fecha_hora_llegada,
        estado=data.estado,
        rampa_embarque=data.rampa_embarque,
    )
    db.add(viaje)
    await db.commit()
    await db.refresh(viaje)
    return viaje


async def update_viaje(db: AsyncSession, id_viaje: int, data: ViajeUpdate) -> Viaje:
    viaje = await get_viaje_by_id(db, id_viaje)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(viaje, key, value)
    await db.commit()
    await db.refresh(viaje)
    return viaje


async def delete_viaje(db: AsyncSession, id_viaje: int) -> dict:
    viaje = await get_viaje_by_id(db, id_viaje)
    await db.delete(viaje)
    await db.commit()
    return {"message": f"Viaje {id_viaje} eliminado"}


# ── Pasajeros ─────────────────────────────────────────────────────────────────

async def get_pasajeros_by_viaje(db: AsyncSession, id_viaje: int) -> list[Pasajero]:
    result = await db.execute(
        select(Pasajero)
        .join(Boleto, Boleto.id_pasajero == Pasajero.id_pasajero)
        .where(Boleto.id_viaje == id_viaje)
    )
    return list(result.scalars().all())


async def get_all_pasajeros(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Pasajero]:
    result = await db.execute(select(Pasajero).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_pasajeros_by_agencia(db: AsyncSession, id_agencia: int, skip: int = 0, limit: int = 100) -> list[Pasajero]:
    result = await db.execute(
        select(Pasajero)
        .join(Boleto, Boleto.id_pasajero == Pasajero.id_pasajero)
        .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
        .join(Bus, Bus.id_bus == Viaje.id_bus)
        .where(Bus.id_agencia == id_agencia)
        .distinct()
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())

async def get_boletos_by_agencia(db: AsyncSession, id_agencia: int, skip: int = 0, limit: int = 100) -> list[Boleto]:
    result = await db.execute(
        select(Boleto)
        .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
        .join(Bus, Bus.id_bus == Viaje.id_bus)
        .where(Bus.id_agencia == id_agencia)
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_pasajero_by_id(db: AsyncSession, id_pasajero: int) -> Pasajero:
    result = await db.execute(select(Pasajero).where(Pasajero.id_pasajero == id_pasajero))
    pasajero = result.scalar_one_or_none()
    if not pasajero:
        raise NotFoundException(f"Pasajero {id_pasajero} no encontrado")
    return pasajero


async def create_pasajero(db: AsyncSession, data: PasajeroCreate) -> Pasajero:
    pasajero = Pasajero(
        id_usuario=data.id_usuario,
        id_tipo_documento=data.id_tipo_documento,
        numero_documento=data.numero_documento,
        nombres=data.nombres,
        apellido_paterno=data.apellido_paterno,
        apellido_materno=data.apellido_materno,
        fecha_nacimiento=data.fecha_nacimiento,
    )
    db.add(pasajero)
    await db.commit()
    await db.refresh(pasajero)
    return pasajero


async def update_pasajero(db: AsyncSession, id_pasajero: int, data: PasajeroUpdate) -> Pasajero:
    pasajero = await get_pasajero_by_id(db, id_pasajero)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(pasajero, key, value)
    await db.commit()
    await db.refresh(pasajero)
    return pasajero


async def delete_pasajero(db: AsyncSession, id_pasajero: int) -> dict:
    pasajero = await get_pasajero_by_id(db, id_pasajero)
    await db.delete(pasajero)
    await db.commit()
    return {"message": f"Pasajero {id_pasajero} eliminado"}


# ── Boletos ───────────────────────────────────────────────────────────────────

async def get_boletos_by_viaje(db: AsyncSession, id_viaje: int) -> list[Boleto]:
    result = await db.execute(select(Boleto).where(Boleto.id_viaje == id_viaje))
    return list(result.scalars().all())


async def get_all_boletos(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Boleto]:
    result = await db.execute(select(Boleto).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_boleto_by_id(db: AsyncSession, id_boleto: int) -> Boleto:
    result = await db.execute(select(Boleto).where(Boleto.id_boleto == id_boleto))
    boleto = result.scalar_one_or_none()
    if not boleto:
        raise NotFoundException(f"Boleto {id_boleto} no encontrado")
    return boleto


async def create_boleto(db: AsyncSession, data: BoletoCreate) -> Boleto:
    boleto = Boleto(
        id_viaje=data.id_viaje,
        id_usuario=data.id_usuario,
        id_pasajero=data.id_pasajero,
        id_asiento=data.id_asiento,
        email_contacto=data.email_contacto,
        canal=data.canal,
        codigo_qr=data.codigo_qr,
        precio_final=data.precio_final,
    )
    db.add(boleto)
    await db.commit()
    await db.refresh(boleto)
    return boleto


async def update_boleto(db: AsyncSession, id_boleto: int, data: BoletoUpdate) -> Boleto:
    boleto = await get_boleto_by_id(db, id_boleto)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(boleto, key, value)
    await db.commit()
    await db.refresh(boleto)
    return boleto


async def delete_boleto(db: AsyncSession, id_boleto: int) -> dict:
    boleto = await get_boleto_by_id(db, id_boleto)
    await db.delete(boleto)
    await db.commit()
    return {"message": f"Boleto {id_boleto} eliminado"}
