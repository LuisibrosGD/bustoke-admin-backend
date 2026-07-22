from pydantic import ValidationError
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.flota.models import AmenidadBus, Asiento, Bus
from app.modules.flota.schemas import (
    AmenidadCreate,
    AsientoCreate,
    AsientoUpdate,
    BusCreate,
    BusUpdate,
)
from app.modules.viajes.models import Viaje


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


async def bulk_create_buses(db: AsyncSession, id_agencia: int, rows: list[dict]) -> dict:
    """Carga masiva de buses desde un Excel ya parseado (ver app/core/excel.py).
    Reutiliza create_bus() fila por fila, así que hereda su validación de placa
    duplicada (ConflictException -> se cuenta como omitido, no como error)."""
    success = 0
    skipped = 0
    errors: list[dict] = []
    for i, row in enumerate(rows, start=2):  # fila 1 = encabezados
        try:
            placa = str(row.get("Placa") or "").strip().upper()
            pisos_raw = row.get("Cantidad de Pisos")

            if not placa:
                raise ValueError("Placa es requerida")
            try:
                cantidad_pisos = int(pisos_raw) if pisos_raw not in (None, "") else 1
            except (TypeError, ValueError):
                raise ValueError(f"Cantidad de Pisos '{pisos_raw}' no es un número válido")
            if cantidad_pisos not in (1, 2):
                raise ValueError("Cantidad de Pisos debe ser 1 o 2")

            data = BusCreate(id_agencia=id_agencia, placa=placa, cantidad_pisos=cantidad_pisos)
            await create_bus(db, data)
            success += 1
        except ConflictException:
            skipped += 1
        except ValidationError as e:
            errors.append({"row": i, "message": e.errors()[0]["msg"]})
        except Exception as e:
            await db.rollback()
            errors.append({"row": i, "message": str(e)})

    return {
        "totalProcessed": len(rows),
        "successCount": success,
        "skippedCount": skipped,
        "errorCount": len(errors),
        "errors": errors,
    }


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

    tiene_viajes = await db.execute(
        select(func.count()).select_from(Viaje).where(Viaje.id_bus == id_bus)
    )
    if tiene_viajes.scalar() > 0:
        raise ConflictException(
            f"No se puede eliminar el bus {id_bus}: tiene viajes asociados"
        )

    # Sin viajes no puede haber boletos que dependan de sus asientos (todo
    # boleto requiere un viaje, y el viaje ya fija el bus). Los asientos y
    # amenidades son solo configuración del bus, sin valor propio: se
    # eliminan junto con él.
    await db.execute(delete(Asiento).where(Asiento.id_bus == id_bus))
    await db.execute(delete(AmenidadBus).where(AmenidadBus.id_bus == id_bus))
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
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise ConflictException(
            f"No se puede eliminar el asiento {id_asiento}: tiene boletos vendidos asociados"
        ) from e
    return {"message": f"Asiento {id_asiento} eliminado"}


# ── Amenidades ────────────────────────────────────────────────────────────────

async def get_amenidades_by_bus(db: AsyncSession, id_bus: int) -> list[AmenidadBus]:
    result = await db.execute(select(AmenidadBus).where(AmenidadBus.id_bus == id_bus))
    return list(result.scalars().all())


async def replace_amenidades(db: AsyncSession, id_bus: int, data: list[AmenidadCreate]) -> list[AmenidadBus]:
    """Reemplaza todas las amenidades del bus por el set nuevo. A diferencia
    de los asientos, nada hace FK a amenidades_bus, así que un borrar-y-
    recrear completo es seguro (sin el riesgo de boletos vendidos)."""
    await db.execute(delete(AmenidadBus).where(AmenidadBus.id_bus == id_bus))
    nuevas = [
        AmenidadBus(
            id_bus=id_bus,
            tipo=item.tipo,
            piso=item.piso,
            coord_x=item.coord_x,
            coord_y=item.coord_y,
        )
        for item in data
    ]
    db.add_all(nuevas)
    await db.commit()
    for a in nuevas:
        await db.refresh(a)
    return nuevas
