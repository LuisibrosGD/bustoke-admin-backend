from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.rutas.models import Ruta, TarifaRuta
from app.modules.rutas.schemas import RutaCreate, RutaOut, RutaUpdate, TarifaRutaCreate, TarifaRutaUpdate
from app.modules.terminales.models import Terminal


async def _enriquecer_rutas(db: AsyncSession, rutas: list[Ruta]) -> list[RutaOut]:
    ids = {r.id_terminal_origen for r in rutas} | {r.id_terminal_destino for r in rutas}
    result = await db.execute(select(Terminal).where(Terminal.id_terminal.in_(ids)))
    terminals = {t.id_terminal: t.nombre for t in result.scalars().all()}
    return [
        RutaOut(
            id=r.id_ruta,
            id_agencia=r.id_agencia,
            id_terminal_origen=r.id_terminal_origen,
            id_terminal_destino=r.id_terminal_destino,
            tarifa_base=r.tarifa_base,
            terminal_origen_nombre=terminals.get(r.id_terminal_origen),
            terminal_destino_nombre=terminals.get(r.id_terminal_destino),
        )
        for r in rutas
    ]


# ── Rutas ─────────────────────────────────────────────────────────────────────

async def get_all_rutas(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[RutaOut]:
    result = await db.execute(select(Ruta).offset(skip).limit(limit))
    rutas = list(result.scalars().all())
    return await _enriquecer_rutas(db, rutas)


async def get_rutas_by_agencia(db: AsyncSession, id_agencia: int) -> list[RutaOut]:
    result = await db.execute(select(Ruta).where(Ruta.id_agencia == id_agencia))
    rutas = list(result.scalars().all())
    return await _enriquecer_rutas(db, rutas)


async def get_ruta_by_id(db: AsyncSession, id_ruta: int) -> RutaOut:
    result = await db.execute(select(Ruta).where(Ruta.id_ruta == id_ruta))
    ruta = result.scalar_one_or_none()
    if not ruta:
        raise NotFoundException(f"Ruta {id_ruta} no encontrada")
    enriched = await _enriquecer_rutas(db, [ruta])
    return enriched[0]


async def create_ruta(db: AsyncSession, data: RutaCreate) -> RutaOut:
    ruta = Ruta(
        id_agencia=data.id_agencia,
        id_terminal_origen=data.id_terminal_origen,
        id_terminal_destino=data.id_terminal_destino,
        tarifa_base=data.tarifa_base,
    )
    db.add(ruta)
    await db.commit()
    await db.refresh(ruta)
    enriched = await _enriquecer_rutas(db, [ruta])
    return enriched[0]


async def get_ruta_by_id_raw(db: AsyncSession, id_ruta: int) -> Ruta:
    result = await db.execute(select(Ruta).where(Ruta.id_ruta == id_ruta))
    ruta = result.scalar_one_or_none()
    if not ruta:
        raise NotFoundException(f"Ruta {id_ruta} no encontrada")
    return ruta


async def update_ruta(db: AsyncSession, id_ruta: int, data: RutaUpdate) -> RutaOut:
    ruta = await get_ruta_by_id_raw(db, id_ruta)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(ruta, key, value)
    await db.commit()
    await db.refresh(ruta)
    enriched = await _enriquecer_rutas(db, [ruta])
    return enriched[0]


async def delete_ruta(db: AsyncSession, id_ruta: int) -> dict:
    ruta = await get_ruta_by_id_raw(db, id_ruta)
    await db.delete(ruta)
    await db.commit()
    return {"message": f"Ruta {id_ruta} eliminada"}


# ── TarifasRuta ───────────────────────────────────────────────────────────────

async def get_tarifas_by_ruta(db: AsyncSession, id_ruta: int) -> list[TarifaRuta]:
    result = await db.execute(select(TarifaRuta).where(TarifaRuta.id_ruta == id_ruta))
    return list(result.scalars().all())


async def get_tarifa_by_id(db: AsyncSession, id_tarifa: int) -> TarifaRuta:
    result = await db.execute(select(TarifaRuta).where(TarifaRuta.id_tarifa == id_tarifa))
    tarifa = result.scalar_one_or_none()
    if not tarifa:
        raise NotFoundException(f"Tarifa {id_tarifa} no encontrada")
    return tarifa


async def create_tarifa(db: AsyncSession, data: TarifaRutaCreate) -> TarifaRuta:
    tarifa = TarifaRuta(
        id_ruta=data.id_ruta,
        tipo_servicio=data.tipo_servicio,
        precio=data.precio,
    )
    db.add(tarifa)
    await db.commit()
    await db.refresh(tarifa)
    return tarifa


async def update_tarifa(db: AsyncSession, id_tarifa: int, data: TarifaRutaUpdate) -> TarifaRuta:
    tarifa = await get_tarifa_by_id(db, id_tarifa)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(tarifa, key, value)
    await db.commit()
    await db.refresh(tarifa)
    return tarifa


async def delete_tarifa(db: AsyncSession, id_tarifa: int) -> dict:
    tarifa = await get_tarifa_by_id(db, id_tarifa)
    await db.delete(tarifa)
    await db.commit()
    return {"message": f"Tarifa {id_tarifa} eliminada"}
