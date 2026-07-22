from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.excel import export_excel  # noqa: F401 (reexportado para reportes/router.py)

# Fragmento de comisión reutilizado por reporte_ventas y reporte_financiero:
# ambos calculan la comisión vigente de la agencia a la fecha de emisión del boleto.
# Es por-boleto (sin agregar): cada reporte devuelve una fila por venta, no un
# resumen agrupado por agencia/ruta/periodo.
_COMISION_JOIN = """
    LEFT JOIN configuracion_comisiones cc
        ON cc.id_agencia = a.id_agencia
       AND cc.fecha_inicio <= b.fecha_emision
       AND (cc.fecha_fin IS NULL OR cc.fecha_fin >= b.fecha_emision)
"""
_COMISION_EXPR = "COALESCE(b.precio_final * cc.porcentaje_comision / 100, 0)"


async def _fetch_paginated(
    db: AsyncSession,
    base_query_sql: str,
    order_by_sql: str,
    params: dict[str, Any],
    page: int,
    limit: int,
):
    """Ejecuta `base_query_sql` (un SELECT sin ORDER BY/LIMIT) paginado con
    LIMIT/OFFSET, devolviendo también el total de filas sin paginar (vía
    COUNT(*) OVER()) para que el frontend pueda calcular totalPages real."""
    offset = (page - 1) * limit
    sql = text(f"""
        WITH base AS (
            {base_query_sql}
        )
        SELECT base.*, COUNT(*) OVER() AS __total_count
        FROM base
        ORDER BY {order_by_sql}
        LIMIT :__limit OFFSET :__offset
    """)
    result = await db.execute(sql, {**params, "__limit": limit, "__offset": offset})
    rows = result.mappings().all()
    total = rows[0]["__total_count"] if rows else 0
    return rows, total


async def reporte_ventas(
    db: AsyncSession,
    id_agencia: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    id_ruta: Optional[str] = None,
    estado_pago: Optional[str] = None,
    metodo_pago: Optional[str] = None,
    canal_venta: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    filters = []
    params: dict[str, Any] = {}

    if id_agencia:
        filters.append("a.id_agencia = :id_agencia")
        params["id_agencia"] = id_agencia
    if fecha_inicio:
        filters.append("b.fecha_emision >= :fecha_inicio")
        params["fecha_inicio"] = datetime.fromisoformat(fecha_inicio)
    if fecha_fin:
        filters.append("b.fecha_emision <= :fecha_fin")
        params["fecha_fin"] = datetime.fromisoformat(fecha_fin)
    if id_ruta:
        ids = [x.strip() for x in id_ruta.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":ruta_{i}" for i in range(len(ids)))
            filters.append(f"v.id_ruta IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"ruta_{i}"] = int(val)
    if canal_venta:
        ids = [x.strip() for x in canal_venta.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":canal_{i}" for i in range(len(ids)))
            filters.append(f"b.canal IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"canal_{i}"] = val
    if metodo_pago:
        ids = [x.strip() for x in metodo_pago.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":metodo_{i}" for i in range(len(ids)))
            filters.append(f"pg.metodo IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"metodo_{i}"] = val
    if estado_pago:
        ids = [x.strip() for x in estado_pago.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":epago_{i}" for i in range(len(ids)))
            filters.append(f"pg.estado IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"epago_{i}"] = val

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    # Una fila por boleto (no un resumen agrupado): el frontend pagina y
    # cuenta filas reales, no un agregado por agencia/ruta/mes.
    base_sql = f"""
        SELECT
            a.razon_social                                                AS agencia,
            CONCAT(t_o.nombre, ' → ', t_d.nombre)                        AS ruta,
            v.fecha_hora_salida                                           AS fecha_viaje,
            CONCAT(p.nombres, ' ', p.apellido_paterno)                    AS pasajero,
            b.precio_final                                                AS monto,
            {_COMISION_EXPR}                                              AS comision
        FROM boletos b
        JOIN viajes v   ON b.id_viaje = v.id_viaje
        JOIN rutas r    ON v.id_ruta  = r.id_ruta
        JOIN terminales t_o ON r.id_terminal_origen = t_o.id_terminal
        JOIN terminales t_d ON r.id_terminal_destino = t_d.id_terminal
        JOIN agencias a ON r.id_agencia = a.id_agencia
        JOIN pasajeros p ON b.id_pasajero = p.id_pasajero
        LEFT JOIN pagos pg ON pg.id_boleto = b.id_boleto
        {_COMISION_JOIN}
        {where_clause}
    """

    rows, total = await _fetch_paginated(
        db, base_sql, "fecha_viaje DESC, agencia, ruta", params, page, limit
    )
    data = [
        {
            "agencia": row["agencia"],
            "ruta": row["ruta"],
            "fechaViaje": str(row["fecha_viaje"]),
            "pasajero": row["pasajero"],
            "monto": float(row["monto"]),
            "comision": float(row["comision"]),
        }
        for row in rows
    ]
    return data, total


async def reporte_viajes(
    db: AsyncSession,
    id_agencia: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    id_ruta: Optional[str] = None,
    id_bus: Optional[str] = None,
    estado_viaje: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    filters = []
    params: dict[str, Any] = {}

    if id_agencia:
        filters.append("r.id_agencia = :id_agencia")
        params["id_agencia"] = id_agencia
    if fecha_inicio:
        filters.append("v.fecha_hora_salida >= :fecha_inicio")
        params["fecha_inicio"] = datetime.fromisoformat(fecha_inicio)
    if fecha_fin:
        filters.append("v.fecha_hora_salida <= :fecha_fin")
        params["fecha_fin"] = datetime.fromisoformat(fecha_fin)
    if id_ruta:
        ids = [x.strip() for x in id_ruta.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":ruta_{i}" for i in range(len(ids)))
            filters.append(f"v.id_ruta IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"ruta_{i}"] = int(val)
    if id_bus:
        ids = [x.strip() for x in id_bus.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":bus_{i}" for i in range(len(ids)))
            filters.append(f"v.id_bus IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"bus_{i}"] = int(val)
    if estado_viaje:
        ids = [x.strip() for x in estado_viaje.split(",") if x.strip()]
        if ids:
            placeholders = ", ".join(f":eviaje_{i}" for i in range(len(ids)))
            filters.append(f"v.estado IN ({placeholders})")
            for i, val in enumerate(ids):
                params[f"eviaje_{i}"] = val

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    # Ocupación real: se calcula contra la cantidad de asientos del bus
    # (tabla `asientos`), no un supuesto fijo de asientos por piso.
    base_sql = f"""
        SELECT
            v.id_viaje,
            CONCAT(t_o.nombre, ' → ', t_d.nombre) AS ruta,
            v.fecha_hora_salida                    AS fecha_salida,
            v.estado,
            COUNT(b.id_boleto)                     AS total_boletos,
            COALESCE(
                ROUND(
                    COUNT(b.id_boleto)::numeric
                    / NULLIF((SELECT COUNT(*) FROM asientos ast WHERE ast.id_bus = bus.id_bus), 0)
                    * 100,
                    2
                ),
                0
            )                                      AS ocupacion
        FROM viajes v
        JOIN rutas r        ON v.id_ruta              = r.id_ruta
        JOIN terminales t_o ON r.id_terminal_origen   = t_o.id_terminal
        JOIN terminales t_d ON r.id_terminal_destino  = t_d.id_terminal
        JOIN buses bus      ON v.id_bus               = bus.id_bus
        LEFT JOIN boletos b ON b.id_viaje = v.id_viaje AND b.estado = 'activo'
        {where_clause}
        GROUP BY v.id_viaje, ruta, v.fecha_hora_salida, v.estado, bus.id_bus
    """

    rows, total = await _fetch_paginated(db, base_sql, "fecha_salida DESC", params, page, limit)
    data = [
        {
            "idViaje": row["id_viaje"],
            "ruta": row["ruta"],
            "fechaSalida": str(row["fecha_salida"]),
            "estado": row["estado"],
            "totalBoletos": int(row["total_boletos"]),
            "ocupacion": float(row["ocupacion"]),
        }
        for row in rows
    ]
    return data, total


async def reporte_manifiesto_sutran(
    db: AsyncSession, id_viaje: int, id_agencia: Optional[int] = None
) -> list[dict[str, Any]]:
    sql = text("""
        SELECT
            b.id_boleto,
            v.id_viaje,
            p.nombres,
            CONCAT(p.apellido_paterno, ' ', p.apellido_materno)                   AS apellidos,
            p.numero_documento,
            a.numero_asiento                                                      AS asiento,
            tor.nombre                                                            AS origen,
            tdes.nombre                                                           AS destino,
            b.email_contacto,
            b.precio_final
        FROM boletos b
        JOIN pasajeros p ON b.id_pasajero = p.id_pasajero
        JOIN asientos a  ON b.id_asiento  = a.id_asiento
        JOIN viajes v    ON b.id_viaje    = v.id_viaje
        JOIN buses bus   ON v.id_bus      = bus.id_bus
        JOIN rutas r     ON v.id_ruta     = r.id_ruta
        JOIN terminales tor  ON r.id_terminal_origen  = tor.id_terminal
        JOIN terminales tdes ON r.id_terminal_destino = tdes.id_terminal
        WHERE v.id_viaje = :id_viaje
          AND b.estado   = 'activo'
          AND (:id_agencia IS NULL OR bus.id_agencia = :id_agencia)
        ORDER BY a.numero_asiento
    """)
    result = await db.execute(sql, {"id_viaje": id_viaje, "id_agencia": id_agencia})
    rows = result.mappings().all()
    return [
        {
            "idViaje": row["id_viaje"],
            "idBoleto": row["id_boleto"],
            "nombres": row["nombres"],
            "apellidos": row["apellidos"],
            "numeroDocumento": row["numero_documento"],
            "asiento": row["asiento"],
            "origen": row["origen"],
            "destino": row["destino"],
            "emailContacto": row["email_contacto"],
            "precioFinal": float(row["precio_final"]),
        }
        for row in rows
    ]


async def reporte_financiero(
    db: AsyncSession,
    id_agencia: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    filters = []
    params: dict[str, Any] = {}

    if id_agencia:
        filters.append("r.id_agencia = :id_agencia")
        params["id_agencia"] = id_agencia
    if fecha_inicio:
        filters.append("b.fecha_emision >= :fecha_inicio")
        params["fecha_inicio"] = datetime.fromisoformat(fecha_inicio)
    if fecha_fin:
        filters.append("b.fecha_emision <= :fecha_fin")
        params["fecha_fin"] = datetime.fromisoformat(fecha_fin)

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    # Una fila por boleto (no un resumen agrupado por agencia/periodo).
    base_sql = f"""
        SELECT
            a.razon_social                                    AS agencia,
            TO_CHAR(b.fecha_emision, 'YYYY-MM')               AS periodo,
            b.fecha_emision                                   AS fecha,
            b.id_boleto                                        AS id_boleto,
            b.precio_final                                    AS monto,
            {_COMISION_EXPR}                                  AS comision,
            b.precio_final - {_COMISION_EXPR}                 AS neto
        FROM boletos b
        JOIN viajes v   ON b.id_viaje = v.id_viaje
        JOIN rutas r    ON v.id_ruta  = r.id_ruta
        JOIN agencias a ON r.id_agencia = a.id_agencia
        {_COMISION_JOIN}
        {where_clause}
    """

    rows, total = await _fetch_paginated(
        db, base_sql, "fecha DESC, agencia", params, page, limit
    )
    data = [
        {
            "agencia": row["agencia"],
            "periodo": row["periodo"],
            "fecha": str(row["fecha"]),
            "idBoleto": row["id_boleto"],
            "monto": float(row["monto"]),
            "comision": float(row["comision"]),
            "neto": float(row["neto"]),
        }
        for row in rows
    ]
    return data, total
