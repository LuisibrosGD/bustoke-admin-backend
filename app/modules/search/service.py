import asyncio

from sqlalchemy import or_, select

from app.database import AsyncSessionLocal
from app.modules.agencias.models import Agencia
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.flota.models import Bus
from app.modules.reclamos.models import Reclamo
from app.modules.rutas.models import Ruta
from app.modules.terminales.models import Terminal
from app.modules.viajes.models import Boleto, Pasajero, Viaje

LIMIT_PER_CATEGORY = 5


def _escape_like(value: str) -> str:
    """Escapa % y _ para que ILIKE los trate como literales, no comodines."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _estado_value(estado) -> str:
    return estado.value if hasattr(estado, "value") else str(estado)


async def _search_agencias(term: str, is_superadmin: bool) -> tuple[str, list[dict]]:
    if not is_superadmin:
        return "agencias", []
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Agencia)
                .where(or_(Agencia.razon_social.ilike(term), Agencia.ruc.ilike(term)))
                .limit(LIMIT_PER_CATEGORY)
            )
        ).scalars().all()
    return "agencias", [
        {"id": a.id_agencia, "title": a.razon_social, "subtitle": f"RUC {a.ruc}", "url": f"/agencias/{a.id_agencia}"}
        for a in rows
    ]


async def _search_viajes(term: str, q: str, id_agencia: int | None) -> tuple[str, list[dict]]:
    viaje_conditions = [Viaje.rampa_embarque.ilike(term)]
    if q.isdigit():
        viaje_conditions.append(Viaje.id_viaje == int(q))
    stmt = select(Viaje).join(Ruta, Ruta.id_ruta == Viaje.id_ruta).where(or_(*viaje_conditions))
    if id_agencia:
        stmt = stmt.where(Ruta.id_agencia == id_agencia)
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(stmt.order_by(Viaje.id_viaje.desc()).limit(LIMIT_PER_CATEGORY))
        ).scalars().all()
    return "viajes", [
        {
            "id": v.id_viaje,
            "title": f"Viaje #{v.id_viaje}",
            "subtitle": f"Sale {v.fecha_hora_salida.strftime('%d/%m/%Y %H:%M')} · {v.rampa_embarque}",
            "url": f"/viajes/{v.id_viaje}",
        }
        for v in rows
    ]


async def _search_buses(term: str, id_agencia: int | None) -> tuple[str, list[dict]]:
    stmt = select(Bus).where(Bus.placa.ilike(term))
    if id_agencia:
        stmt = stmt.where(Bus.id_agencia == id_agencia)
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(stmt.limit(LIMIT_PER_CATEGORY))).scalars().all()
    return "buses", [
        {"id": b.id_bus, "title": b.placa, "subtitle": f"{b.cantidad_pisos} piso(s)", "url": f"/flota/{b.id_bus}"}
        for b in rows
    ]


async def _search_terminales(term: str, id_agencia: int | None) -> tuple[str, list[dict]]:
    stmt = select(Terminal).where(or_(Terminal.nombre.ilike(term), Terminal.direccion.ilike(term)))
    if id_agencia:
        stmt = stmt.join(
            AgenciaTerminal, AgenciaTerminal.id_terminal == Terminal.id_terminal
        ).where(AgenciaTerminal.id_agencia == id_agencia)
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(stmt.limit(LIMIT_PER_CATEGORY))).scalars().all()
    return "terminales", [
        {"id": t.id_terminal, "title": t.nombre, "subtitle": t.direccion, "url": f"/terminales/{t.id_terminal}"}
        for t in rows
    ]


async def _search_reclamos(term: str, id_agencia: int | None) -> tuple[str, list[dict]]:
    stmt = select(Reclamo).where(Reclamo.motivo.ilike(term))
    if id_agencia:
        stmt = stmt.where(Reclamo.id_agencia == id_agencia)
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(stmt.order_by(Reclamo.fecha_creacion.desc()).limit(LIMIT_PER_CATEGORY))
        ).scalars().all()
    return "reclamos", [
        {"id": r.id_reclamo, "title": r.motivo, "subtitle": _estado_value(r.estado), "url": f"/reclamos/{r.id_reclamo}"}
        for r in rows
    ]


async def _search_pasajeros(term: str, id_agencia: int | None) -> tuple[str, list[dict]]:
    conditions = or_(
        Pasajero.nombres.ilike(term),
        Pasajero.apellido_paterno.ilike(term),
        Pasajero.apellido_materno.ilike(term),
        Pasajero.numero_documento.ilike(term),
    )
    if id_agencia:
        stmt = (
            select(Pasajero)
            .join(Boleto, Boleto.id_pasajero == Pasajero.id_pasajero)
            .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(conditions)
            .where(Ruta.id_agencia == id_agencia)
            .distinct()
        )
    else:
        stmt = select(Pasajero).where(conditions)
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(stmt.limit(LIMIT_PER_CATEGORY))).scalars().all()
    return "pasajeros", [
        {
            "id": p.id_pasajero,
            "title": f"{p.nombres} {p.apellido_paterno} {p.apellido_materno}",
            "subtitle": f"Doc. {p.numero_documento}",
            "url": "/pasajeros",
        }
        for p in rows
    ]


async def _search_boletos(term: str, id_agencia: int | None) -> tuple[str, list[dict]]:
    if id_agencia:
        stmt = (
            select(Boleto)
            .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(Boleto.codigo_qr.ilike(term))
            .where(Ruta.id_agencia == id_agencia)
        )
    else:
        stmt = select(Boleto).where(Boleto.codigo_qr.ilike(term))
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(stmt.limit(LIMIT_PER_CATEGORY))).scalars().all()
    return "boletos", [
        {"id": b.id_boleto, "title": b.codigo_qr, "subtitle": f"Viaje #{b.id_viaje}", "url": f"/viajes/{b.id_viaje}/boletos"}
        for b in rows
    ]


async def search(q: str, id_agencia: int | None, is_superadmin: bool) -> dict:
    """Busca en paralelo en varias tablas, cada una con su propia sesión/conexión
    del pool. Un `AsyncSession` no soporta consultas concurrentes sobre la misma
    conexión, así que cada categoría abre y cierra la suya (pool_size=10 en
    database.py da margen de sobra para las 7 consultas simultáneas)."""
    term = f"%{_escape_like(q)}%"

    category_results = await asyncio.gather(
        _search_agencias(term, is_superadmin),
        _search_viajes(term, q, id_agencia),
        _search_buses(term, id_agencia),
        _search_terminales(term, id_agencia),
        _search_reclamos(term, id_agencia),
        _search_pasajeros(term, id_agencia),
        _search_boletos(term, id_agencia),
    )

    results = {name: items for name, items in category_results if items}
    return {"query": q, "results": results}
