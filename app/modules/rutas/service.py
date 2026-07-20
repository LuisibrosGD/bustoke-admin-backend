from decimal import Decimal, InvalidOperation

from sqlalchemy import or_, select
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


async def get_rutas_scoped(
    db: AsyncSession, id_agencia: int | None = None, id_terminal: int | None = None
) -> list[RutaOut]:
    """Rutas filtradas por agencia y, si aplica, por terminal (origen o
    destino) — usado por admin_terminal."""
    query = select(Ruta)
    if id_agencia is not None:
        query = query.where(Ruta.id_agencia == id_agencia)
    if id_terminal is not None:
        query = query.where(
            or_(Ruta.id_terminal_origen == id_terminal, Ruta.id_terminal_destino == id_terminal)
        )
    result = await db.execute(query)
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


async def bulk_create_rutas(db: AsyncSession, id_agencia: int, rows: list[dict]) -> dict:
    """Carga masiva de rutas desde un Excel ya parseado (ver app/core/excel.py).
    Reutiliza create_ruta() fila por fila, así que hereda toda su validación."""
    terminales_result = await db.execute(select(Terminal.id_terminal, Terminal.nombre))
    terminales_by_name = {nombre.strip().lower(): tid for tid, nombre in terminales_result.all()}

    success = 0
    errors: list[dict] = []
    for i, row in enumerate(rows, start=2):  # fila 1 = encabezados
        try:
            origen_nombre = str(row.get("Terminal Origen") or "").strip()
            destino_nombre = str(row.get("Terminal Destino") or "").strip()
            tarifa_raw = row.get("Tarifa Base")

            id_origen = terminales_by_name.get(origen_nombre.lower())
            if not id_origen:
                raise ValueError(f"Terminal origen '{origen_nombre}' no existe")
            id_destino = terminales_by_name.get(destino_nombre.lower())
            if not id_destino:
                raise ValueError(f"Terminal destino '{destino_nombre}' no existe")
            if tarifa_raw is None or str(tarifa_raw).strip() == "":
                raise ValueError("Tarifa Base es requerida")
            try:
                tarifa_base = Decimal(str(tarifa_raw))
            except InvalidOperation:
                raise ValueError(f"Tarifa Base '{tarifa_raw}' no es un número válido")

            data = RutaCreate(
                id_agencia=id_agencia,
                id_terminal_origen=id_origen,
                id_terminal_destino=id_destino,
                tarifa_base=tarifa_base,
            )
            await create_ruta(db, data)
            success += 1
        except Exception as e:
            await db.rollback()
            errors.append({"row": i, "message": str(e)})

    return {
        "totalProcessed": len(rows),
        "successCount": success,
        "skippedCount": 0,
        "errorCount": len(errors),
        "errors": errors,
    }


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
