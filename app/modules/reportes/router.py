from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.dependencies import AdminOrSuper, DbDep
from app.modules.reportes import service
from app.modules.reportes.schemas import ReporteGenericoOut

router = APIRouter(prefix="/reports", tags=["Reportes"])

SLUGS = {"ventas", "viajes", "manifiesto-sutran"}


@router.get("/{slug}", response_model=ReporteGenericoOut)
async def get_reporte(
    slug: str,
    db: DbDep,
    _: AdminOrSuper,
    id_agencia: Optional[int] = Query(None),
    id_viaje: Optional[int] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
):
    if slug == "ventas":
        data = await service.reporte_ventas(db, id_agencia, fecha_inicio, fecha_fin)
    elif slug == "viajes":
        data = await service.reporte_viajes(db, id_agencia, fecha_inicio, fecha_fin)
    elif slug == "manifiesto-sutran":
        if not id_viaje:
            from app.core.exceptions import BadRequestException
            raise BadRequestException("Se requiere id_viaje para el manifiesto SUTRAN")
        data = await service.reporte_manifiesto_sutran(db, id_viaje)
    else:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Reporte '{slug}' no encontrado. Slugs válidos: {SLUGS}")

    return ReporteGenericoOut(slug=slug, data=data, total=len(data))


@router.get("/{slug}/export/excel")
async def export_reporte_excel(
    slug: str,
    db: DbDep,
    _: AdminOrSuper,
    id_agencia: Optional[int] = Query(None),
    id_viaje: Optional[int] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
):
    if slug == "ventas":
        data = await service.reporte_ventas(db, id_agencia, fecha_inicio, fecha_fin)
        sheet = "Ventas"
    elif slug == "viajes":
        data = await service.reporte_viajes(db, id_agencia, fecha_inicio, fecha_fin)
        sheet = "Viajes"
    elif slug == "manifiesto-sutran":
        if not id_viaje:
            from app.core.exceptions import BadRequestException
            raise BadRequestException("Se requiere id_viaje para el manifiesto SUTRAN")
        data = await service.reporte_manifiesto_sutran(db, id_viaje)
        sheet = f"Manifiesto-Viaje-{id_viaje}"
    else:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Reporte '{slug}' no encontrado")

    excel_bytes = await service.export_excel(data, sheet)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{slug}.xlsx"'},
    )
