from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agencias.models import Agencia
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.flota.models import Bus
from app.modules.rutas.models import Ruta
from app.modules.viajes.models import Boleto, Viaje


async def get_dashboard_data(db: AsyncSession, id_agencia: int | None = None) -> dict:
    now = datetime.now()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    base_agencia_filter = Ruta.id_agencia == id_agencia if id_agencia else True

    # ── KPIs ───────────────────────────────────────────────────────────
    if id_agencia:
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
            select(func.count(Ruta.id_ruta)).where(base_agencia_filter)
        )
    ).scalar() or 0

    viajes_this_month = (
        await db.execute(
            select(func.count(Viaje.id_viaje))
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_agencia_filter)
            .where(Viaje.fecha_hora_salida >= first_of_month)
        )
    ).scalar() or 0

    pasajeros_this_month = (
        await db.execute(
            select(func.count(Boleto.id_boleto))
            .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_agencia_filter)
            .where(Boleto.fecha_emision >= first_of_month)
        )
    ).scalar() or 0

    recaudacion = (
        await db.execute(
            select(func.coalesce(func.sum(Boleto.precio_final), 0))
            .join(Viaje, Viaje.id_viaje == Boleto.id_viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_agencia_filter)
            .where(Boleto.fecha_emision >= first_of_month)
        )
    ).scalar() or 0

    kpis = [
        {"title": "Terminales", "value": str(terminales_count), "subtitle": "Terminales activas"},
        {"title": "Flota", "value": str(buses_count), "subtitle": "Buses operativos"},
        {"title": "Rutas", "value": str(rutas_count), "subtitle": "Rutas activas"},
        {"title": "Viajes", "value": str(viajes_this_month), "subtitle": "Este mes"},
        {"title": "Pasajeros", "value": format(pasajeros_this_month, ","), "subtitle": "Este mes"},
        {"title": "Recaudación", "value": f"S/ {recaudacion:,.0f}", "subtitle": "Este mes"},
    ]

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
            .where(base_agencia_filter)
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
    upcoming = (
        await db.execute(
            select(Viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_agencia_filter)
            .where(Viaje.fecha_hora_salida >= now)
            .where(Viaje.estado == "programado")
            .order_by(Viaje.fecha_hora_salida)
            .limit(5)
        )
    ).scalars().all()

    upcoming_trips = []
    for v in upcoming:
        hora = v.fecha_hora_salida.strftime("%H:%M")
        upcoming_trips.append({
            "hora": hora,
            "origen": "",
            "destino": "",
            "pasajeros": 0,
        })

    # ── Actividades recientes ───────────────────────────────────────────
    recent_viajes = (
        await db.execute(
            select(Viaje)
            .join(Ruta, Ruta.id_ruta == Viaje.id_ruta)
            .where(base_agencia_filter)
            .order_by(Viaje.fecha_hora_salida.desc())
            .limit(5)
        )
    ).scalars().all()

    recent_activities = []
    for i, v in enumerate(recent_viajes):
        diff = now - v.fecha_hora_salida
        if diff.total_seconds() < 3600:
            hora_str = f"Hace {int(diff.total_seconds() // 60)} min"
        elif diff.days < 1:
            hora_str = f"Hace {int(diff.total_seconds() // 3600)} horas"
        else:
            hora_str = f"Hace {diff.days} dias"
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
            .where(base_agencia_filter)
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

    return {
        "kpis": kpis,
        "monthlyTrips": monthly_trips,
        "recentActivities": recent_activities,
        "upcomingTrips": upcoming_trips,
        "alerts": alerts,
    }
