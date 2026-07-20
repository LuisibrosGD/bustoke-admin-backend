from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import terminal_ruta_condition
from app.modules.agencias.models import Agencia
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.flota.models import Bus
from app.modules.reclamos.models import Reclamo
from app.modules.rutas.models import Ruta
from app.modules.soporte.models import TicketSoporte
from app.modules.terminales.models import Terminal
from app.modules.viajes.models import Boleto, Viaje


async def get_dashboard_data(
    db: AsyncSession, id_agencia: int | None = None, id_terminal: int | None = None
) -> dict:
    now = datetime.now()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    base_agencia_filter = Ruta.id_agencia == id_agencia if id_agencia else True
    base_terminal_filter = terminal_ruta_condition(id_terminal) if id_terminal else True
    base_filter = and_(base_agencia_filter, base_terminal_filter)

    # ── Contexto (nombre de agencia/terminal para personalizar el frontend) ──
    context: dict = {}
    if id_terminal:
        terminal_nombre = (
            await db.execute(select(Terminal.nombre).where(Terminal.id_terminal == id_terminal))
        ).scalar()
        agencia_nombre = (
            (await db.execute(select(Agencia.razon_social).where(Agencia.id_agencia == id_agencia))).scalar()
            if id_agencia
            else None
        )
        context = {"label": f"{terminal_nombre} — {agencia_nombre}" if agencia_nombre else terminal_nombre}
    elif id_agencia:
        agencia_nombre = (
            await db.execute(select(Agencia.razon_social).where(Agencia.id_agencia == id_agencia))
        ).scalar()
        context = {"label": agencia_nombre}

    # ── KPIs ───────────────────────────────────────────────────────────
    if id_terminal:
        # Un admin_terminal siempre está restringido a exactamente 1 terminal.
        terminales_count = 1
    elif id_agencia:
        terminales_count = (
            await db.execute(
                select(func.count(AgenciaTerminal.id_terminal))
                .where(AgenciaTerminal.id_agencia == id_agencia)
            )
        ).scalar() or 0
    else:
        terminales_count = (
            await db.execute(select(func.count(AgenciaTerminal.id_terminal)))
        ).scalar() or 0

    # Un bus no está atado a un terminal (circula entre varios), así que
    # para admin_terminal se muestra el total de buses de TODA la agencia,
    # no solo los que pasan por este punto — es una limitación conocida del
    # modelo de datos, no un bug. Ver plan de admin_terminal.
    if id_agencia:
        buses_count = (
            await db.execute(
                select(func.count(Bus.id_bus)).where(Bus.id_agencia == id_agencia)
            )
        ).scalar() or 0
    else:
        buses_count = (
            await db.execute(select(func.count(Bus.id_bus)))
        ).scalar() or 0

    rutas_count = (
        await db.execute(
            select(func.count(Ruta.id_ruta)).where(base_filter)
        )
    ).scalar() or 0

    viajes_this_month = (
        await db.execute(
            select(func.count(Viaje.id_viaje))
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .where(Viaje.fecha_hora_salida >= first_of_month)
        )
    ).scalar() or 0

    pasajeros_this_month = (
        await db.execute(
            select(func.count(Boleto.id_boleto))
            .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .where(Boleto.fecha_emision >= first_of_month)
        )
    ).scalar() or 0

    recaudacion = (
        await db.execute(
            select(func.coalesce(func.sum(Boleto.precio_final), 0))
            .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .where(Boleto.fecha_emision >= first_of_month)
        )
    ).scalar() or 0

    kpis = [
        {"title": "Terminales", "value": str(terminales_count), "subtitle": "Terminales activas"},
        {
            "title": "Flota",
            "value": str(buses_count),
            "subtitle": "Buses de la agencia" if id_terminal else "Buses operativos",
        },
        {"title": "Rutas", "value": str(rutas_count), "subtitle": "Rutas activas"},
        {"title": "Viajes", "value": str(viajes_this_month), "subtitle": "Este mes"},
        {"title": "Pasajeros", "value": format(pasajeros_this_month, ","), "subtitle": "Este mes"},
        {"title": "Recaudación", "value": f"S/ {recaudacion:,.0f}", "subtitle": "Este mes"},
    ]

    # Para admin_terminal, "Terminales" (siempre 1) y "Flota" (de toda la
    # agencia) no aportan nada — se reemplazan por métricas del día en
    # este punto específico.
    if id_terminal:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        viajes_hoy = (
            await db.execute(
                select(func.count(Viaje.id_viaje))
                .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
                .where(base_filter)
                .where(Viaje.fecha_hora_salida >= today_start, Viaje.fecha_hora_salida < today_end)
            )
        ).scalar() or 0
        checkins_pendientes_hoy = (
            await db.execute(
                select(func.count(Boleto.id_boleto))
                .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
                .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
                .where(base_filter)
                .where(Viaje.fecha_hora_salida >= today_start, Viaje.fecha_hora_salida < today_end)
                .where(Boleto.estado_checkin == "pendiente")
                .where(Boleto.estado == "activo")
            )
        ).scalar() or 0
        kpis[0] = {"title": "Viajes hoy", "value": str(viajes_hoy), "subtitle": "Salidas/llegadas de este terminal"}
        kpis[1] = {"title": "Check-ins pendientes", "value": str(checkins_pendientes_hoy), "subtitle": "Boletos de viajes de hoy"}

    # ── Viajes por mes (últimos 12 meses) ──────────────────────────────
    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    monthly_trips = [{"month": "", "viajes": 0} for _ in range(12)]
    lookup: dict[str, int] = {}
    for i in range(12):
        month_offset = now.month - 12 + i
        y = now.year + (month_offset // 12)
        m = (month_offset % 12) + 1
        lookup[f"{y}-{m:02d}"] = i
        monthly_trips[i]["month"] = month_names[m - 1]

    first_offset = now.month - 12
    first_year = now.year + (first_offset // 12)
    first_month = (first_offset % 12) + 1
    twelve_months_ago = datetime(first_year, first_month, 1)

    monthly_rows = (
        await db.execute(
            select(
                func.date_trunc(literal_column("'month'"), Viaje.fecha_hora_salida).label("mes"),
                func.count(Viaje.id_viaje).label("total"),
            )
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .where(Viaje.fecha_hora_salida >= twelve_months_ago)
            .group_by(func.date_trunc(literal_column("'month'"), Viaje.fecha_hora_salida))
            .order_by(func.date_trunc(literal_column("'month'"), Viaje.fecha_hora_salida))
        )
    ).all()
    for row in monthly_rows:
        if hasattr(row.mes, "month") and hasattr(row.mes, "year"):
            key = f"{row.mes.year}-{row.mes.month:02d}"
            idx = lookup.get(key)
            if idx is not None:
                monthly_trips[idx]["viajes"] = row.total

    # ── Próximos viajes ────────────────────────────────────────────────
    upcoming_rows = (
        await db.execute(
            select(Viaje, Ruta.id_terminal_origen, Ruta.id_terminal_destino)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .where(Viaje.fecha_hora_salida >= now)
            .where(Viaje.estado == "programado")
            .order_by(Viaje.fecha_hora_salida)
            .limit(5)
        )
    ).all()

    terminal_ids = {tid for _, o, d in upcoming_rows for tid in (o, d)}
    viaje_ids = [v.id_viaje for v, _, _ in upcoming_rows]

    terminal_names = dict(
        (await db.execute(
            select(Terminal.id_terminal, Terminal.nombre).where(Terminal.id_terminal.in_(terminal_ids))
        )).all()
    ) if terminal_ids else {}

    pasajero_counts = dict(
        (await db.execute(
            select(Boleto.id_viaje, func.count(Boleto.id_boleto))
            .where(Boleto.id_viaje.in_(viaje_ids))
            .where(Boleto.estado == "activo")
            .group_by(Boleto.id_viaje)
        )).all()
    ) if viaje_ids else {}

    upcoming_trips = [{
        "hora": v.fecha_hora_salida.strftime("%H:%M"),
        "origen": terminal_names.get(o, ""),
        "destino": terminal_names.get(d, ""),
        "pasajeros": pasajero_counts.get(v.id_viaje, 0),
    } for v, o, d in upcoming_rows]

    # ── Actividades recientes ───────────────────────────────────────────
    # El modelo Viaje no tiene columna de fecha de creación, así que se usa
    # id_viaje (autoincremental) como proxy del orden de registro. No se
    # puede calcular un "hace X min" a partir de fecha_hora_salida porque
    # es la salida programada del viaje (normalmente futura, no pasada) -
    # eso producía duraciones negativas ("Hace -107477 min"). En su lugar
    # se muestra la fecha/hora de salida programada, que sí es información
    # útil y correcta.
    recent_viajes = (
        await db.execute(
            select(Viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .order_by(Viaje.id_viaje.desc())
            .limit(5)
        )
    ).scalars().all()

    recent_activities = []
    for i, v in enumerate(recent_viajes):
        hora_str = f"Sale: {v.fecha_hora_salida.strftime('%d/%m/%Y %H:%M')}"
        recent_activities.append({
            "id": i + 1,
            "descripcion": f"Viaje #{v.id_viaje} registrado",
            "estado": v.estado.value if hasattr(v.estado, "value") else v.estado,
            "hora": hora_str,
        })

    # ── Alertas ─────────────────────────────────────────────────────────
    alerts = []

    # Buscar viajes cancelados
    cancelados = (
        await db.execute(
            select(func.count(Viaje.id_viaje))
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_filter)
            .where(Viaje.estado == "cancelado")
            .where(Viaje.fecha_hora_salida >= first_of_month)
        )
    ).scalar() or 0
    if cancelados > 0:
        alerts.append({
            "type": "warning",
            "title": f"{cancelados} viaje(s) cancelado(s) este mes",
            "description": "Revisar programacion y disponibilidad de unidades.",
        })

    # Reclamos y tickets de soporte no tienen atribución a terminal, así
    # que esta sección no aplica a admin_terminal.
    if not id_terminal:
        reclamos_abiertos = (
            await db.execute(
                select(func.count(Reclamo.id_reclamo))
                .where(Reclamo.estado == "abierto")
                .where(Reclamo.id_agencia == id_agencia if id_agencia else True)
            )
        ).scalar() or 0
        if reclamos_abiertos > 0:
            alerts.append({
                "type": "warning",
                "title": f"{reclamos_abiertos} reclamo(s) abierto(s)",
                "description": "Revisar reclamos pendientes de atención.",
            })

        tickets_abiertos = (
            await db.execute(
                select(func.count(TicketSoporte.id_ticket_soporte))
                .where(TicketSoporte.estado.in_(["abierto", "en_revision"]))
                .where(TicketSoporte.id_agencia == id_agencia if id_agencia else True)
            )
        ).scalar() or 0
        if tickets_abiertos > 0:
            alerts.append({
                "type": "info",
                "title": f"{tickets_abiertos} ticket(s) de soporte pendiente(s)",
                "description": "Tickets abiertos o en revisión.",
            })

    return {
        "kpis": kpis,
        "context": context,
        "monthlyTrips": monthly_trips,
        "recentActivities": recent_activities,
        "upcomingTrips": upcoming_trips,
        "alerts": alerts,
    }
