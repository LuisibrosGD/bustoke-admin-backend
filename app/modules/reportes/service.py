import io
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException


async def reporte_ventas(
    db: AsyncSession,
    id_agencia: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
) -> list[dict[str, Any]]:
    filters = []
    params: dict[str, Any] = {}

    if id_agencia:
        filters.append("a.id_agencia = :id_agencia")
        params["id_agencia"] = id_agencia
    if fecha_inicio:
        filters.append("b.fecha_emision >= :fecha_inicio")
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        filters.append("b.fecha_emision <= :fecha_fin")
        params["fecha_fin"] = fecha_fin

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    sql = text(f"""
        SELECT
            TO_CHAR(b.fecha_emision, 'YYYY-MM') AS periodo,
            b.canal,
            COUNT(b.id_boleto)                  AS total_boletos,
            SUM(b.precio_final)                 AS total_ventas
        FROM boletos b
        JOIN viajes v ON b.id_viaje = v.id_viaje
        JOIN rutas r  ON v.id_ruta  = r.id_ruta
        JOIN agencias a ON r.id_agencia = a.id_agencia
        {where_clause}
        GROUP BY periodo, b.canal
        ORDER BY periodo DESC, b.canal
    """)

    result = await db.execute(sql, params)
    rows = result.mappings().all()
    return [
        {
            "periodo": row["periodo"],
            "canal": row["canal"],
            "totalBoletos": int(row["total_boletos"]),
            "totalVentas": float(row["total_ventas"]),
        }
        for row in rows
    ]


async def reporte_viajes(
    db: AsyncSession,
    id_agencia: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
) -> list[dict[str, Any]]:
    filters = []
    params: dict[str, Any] = {}

    if id_agencia:
        filters.append("r.id_agencia = :id_agencia")
        params["id_agencia"] = id_agencia
    if fecha_inicio:
        filters.append("v.fecha_hora_salida >= :fecha_inicio")
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        filters.append("v.fecha_hora_salida <= :fecha_fin")
        params["fecha_fin"] = fecha_fin

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    sql = text(f"""
        SELECT
            v.id_viaje,
            CONCAT(t_o.nombre, ' → ', t_d.nombre) AS ruta,
            v.fecha_hora_salida                    AS fecha_salida,
            v.estado,
            COUNT(b.id_boleto)                     AS total_boletos,
            COALESCE(
                ROUND(COUNT(b.id_boleto)::numeric / NULLIF(bus.cantidad_pisos * 50, 0) * 100, 2),
                0
            )                                      AS ocupacion
        FROM viajes v
        JOIN rutas r        ON v.id_ruta              = r.id_ruta
        JOIN terminales t_o ON r.id_terminal_origen   = t_o.id_terminal
        JOIN terminales t_d ON r.id_terminal_destino  = t_d.id_terminal
        JOIN buses bus      ON v.id_bus               = bus.id_bus
        LEFT JOIN boletos b ON b.id_viaje = v.id_viaje AND b.estado = 'activo'
        {where_clause}
        GROUP BY v.id_viaje, ruta, v.fecha_hora_salida, v.estado, bus.cantidad_pisos
        ORDER BY v.fecha_hora_salida DESC
    """)

    result = await db.execute(sql, params)
    rows = result.mappings().all()
    return [
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


async def reporte_manifiesto_sutran(
    db: AsyncSession, id_viaje: int
) -> list[dict[str, Any]]:
    sql = text("""
        SELECT
            b.id_boleto,
            v.id_viaje,
            CONCAT(p.nombres, ' ', p.apellido_paterno, ' ', p.apellido_materno) AS pasajero,
            p.numero_documento,
            a.numero_asiento                                                      AS asiento,
            b.email_contacto,
            b.precio_final
        FROM boletos b
        JOIN pasajeros p ON b.id_pasajero = p.id_pasajero
        JOIN asientos a  ON b.id_asiento  = a.id_asiento
        JOIN viajes v    ON b.id_viaje    = v.id_viaje
        WHERE v.id_viaje = :id_viaje
          AND b.estado   = 'activo'
        ORDER BY a.numero_asiento
    """)
    result = await db.execute(sql, {"id_viaje": id_viaje})
    rows = result.mappings().all()
    return [
        {
            "idViaje": row["id_viaje"],
            "idBoleto": row["id_boleto"],
            "pasajero": row["pasajero"],
            "numeroDocumento": row["numero_documento"],
            "asiento": row["asiento"],
            "emailContacto": row["email_contacto"],
            "precioFinal": float(row["precio_final"]),
        }
        for row in rows
    ]


async def export_excel(data: list[dict[str, Any]], sheet_name: str = "Reporte") -> bytes:
    """Genera un archivo Excel en memoria y devuelve los bytes."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    if not data:
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    headers = list(data[0].keys())
    ws.append(headers)
    for row in data:
        ws.append([row.get(h) for h in headers])

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
