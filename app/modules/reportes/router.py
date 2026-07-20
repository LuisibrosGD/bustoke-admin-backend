from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.dependencies import AdminOrSuper, DbDep, resolve_agencia_scope
from app.modules.reportes import service
from app.modules.reportes.schemas import ReporteGenericoOut

router = APIRouter(prefix="/reports", tags=["Reportes"])

SLUGS = {"ventas", "viajes", "manifiesto-sutran", "financiero"}

# Límite alto usado para exportar a Excel: queremos todas las filas que
# calcen con los filtros, no solo la página actual.
_EXPORT_MAX_ROWS = 1_000_000


async def _run_reporte(
    slug: str,
    db: DbDep,
    id_agencia: Optional[int],
    id_ruta: Optional[str],
    id_bus: Optional[str],
    id_viaje: Optional[int],
    estado_viaje: Optional[str],
    fecha_inicio: Optional[str],
    fecha_fin: Optional[str],
    estado_pago: Optional[str],
    metodo_pago: Optional[str],
    canal_venta: Optional[str],
    page: int,
    limit: int,
) -> tuple[list[dict[str, Any]], int]:
    if slug == "ventas":
        return await service.reporte_ventas(
            db, id_agencia, fecha_inicio, fecha_fin,
            id_ruta, estado_pago, metodo_pago, canal_venta,
            page, limit,
        )
    if slug == "viajes":
        return await service.reporte_viajes(
            db, id_agencia, fecha_inicio, fecha_fin,
            id_ruta, id_bus, estado_viaje,
            page, limit,
        )
    if slug == "manifiesto-sutran":
        if not id_viaje:
            from app.core.exceptions import BadRequestException
            raise BadRequestException("Se requiere id_viaje para el manifiesto SUTRAN")
        data = await service.reporte_manifiesto_sutran(db, id_viaje, id_agencia)
        return data, len(data)
    if slug == "financiero":
        return await service.reporte_financiero(
            db, id_agencia, fecha_inicio, fecha_fin,
            page, limit,
        )
    from app.core.exceptions import NotFoundException
    raise NotFoundException(f"Reporte '{slug}' no encontrado. Slugs válidos: {SLUGS}")


@router.get("/{slug}", response_model=ReporteGenericoOut)
async def get_reporte(
    slug: str,
    db: DbDep,
    current_user: AdminOrSuper,
    id_agencia: Optional[int] = Query(None),
    id_ruta: Optional[str] = Query(None),
    id_bus: Optional[str] = Query(None),
    id_viaje: Optional[int] = Query(None),
    estado_viaje: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    estado_pago: Optional[str] = Query(None),
    metodo_pago: Optional[str] = Query(None),
    canal_venta: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    data, total = await _run_reporte(
        slug, db, id_agencia, id_ruta, id_bus, id_viaje, estado_viaje,
        fecha_inicio, fecha_fin, estado_pago, metodo_pago, canal_venta,
        page, limit,
    )
    if slug == "manifiesto-sutran":
        # No se pagina: siempre trae el manifiesto completo del viaje.
        page, limit = 1, max(total, 1)
    total_pages = max(1, (total + limit - 1) // limit) if total else 1
    return ReporteGenericoOut(
        slug=slug, data=data, total=total, page=page, limit=limit, totalPages=total_pages,
    )


@router.get("/{slug}/export/excel")
async def export_reporte_excel(
    slug: str,
    db: DbDep,
    current_user: AdminOrSuper,
    id_agencia: Optional[int] = Query(None),
    id_ruta: Optional[str] = Query(None),
    id_bus: Optional[str] = Query(None),
    id_viaje: Optional[int] = Query(None),
    estado_viaje: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    estado_pago: Optional[str] = Query(None),
    metodo_pago: Optional[str] = Query(None),
    canal_venta: Optional[str] = Query(None),
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    sheet_names = {
        "ventas": "Ventas",
        "viajes": "Viajes",
        "manifiesto-sutran": f"Manifiesto-Viaje-{id_viaje}",
        "financiero": "Financiero",
    }
    if slug not in SLUGS:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Reporte '{slug}' no encontrado")

    data, _ = await _run_reporte(
        slug, db, id_agencia, id_ruta, id_bus, id_viaje, estado_viaje,
        fecha_inicio, fecha_fin, estado_pago, metodo_pago, canal_venta,
        page=1, limit=_EXPORT_MAX_ROWS,
    )
    excel_bytes = await service.export_excel(data, sheet_names[slug])
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{slug}.xlsx"'},
    )
