from datetime import datetime

from fastapi import APIRouter, File, Query, Response, UploadFile

from app.core.exceptions import BadRequestException
from app.core.excel import export_excel, read_excel_rows
from app.dependencies import AdminOrSuper, DbDep, resolve_agencia_scope
from app.modules.flota import service
from app.modules.flota.schemas import (
    AmenidadOut,
    AsientoCreate,
    AsientoOut,
    AsientoUpdate,
    BusCreate,
    BusOut,
    BusUpdate,
    ReemplazarAmenidadesRequest,
)

router = APIRouter(prefix="/admin/flota", tags=["Flota"])


# ── Buses ─────────────────────────────────────────────────────────────────────

@router.get("/buses", response_model=list[BusOut])
async def list_buses(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    if id_agencia:
        return await service.get_buses_by_agencia(db, id_agencia)
    return await service.get_all_buses(db, skip, limit)


@router.get("/buses/{id_bus}", response_model=BusOut)
async def get_bus(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.get_bus_by_id(db, id_bus)


@router.post("/buses", response_model=BusOut, status_code=201)
async def create_bus(body: BusCreate, db: DbDep, current_user: AdminOrSuper):
    body.id_agencia = resolve_agencia_scope(current_user, body.id_agencia)
    return await service.create_bus(db, body)


@router.put("/buses/{id_bus}", response_model=BusOut)
async def update_bus(id_bus: int, body: BusUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_bus(db, id_bus, body)


@router.post("/buses/carga-masiva")
async def bulk_upload_buses(
    db: DbDep,
    current_user: AdminOrSuper,
    file: UploadFile = File(...),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    if not id_agencia:
        raise BadRequestException("Selecciona una agencia para la carga masiva")
    rows = read_excel_rows(await file.read())
    result = await service.bulk_create_buses(db, id_agencia, rows)
    result["file"] = {
        "resourceId": "",
        "originalName": file.filename,
        "uploadedBy": current_user.get("email", ""),
        "uploadedAt": datetime.now().isoformat(),
    }
    return result


@router.get("/buses/carga-masiva/plantilla")
async def descargar_plantilla_buses(_: AdminOrSuper):
    data = [{"Placa": "ABC-123", "Cantidad de Pisos": 2}]
    content = await export_excel(data, sheet_name="Buses")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_buses.xlsx"},
    )


@router.delete("/buses/{id_bus}")
async def delete_bus(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_bus(db, id_bus)


# ── Asientos ──────────────────────────────────────────────────────────────────

@router.get("/buses/{id_bus}/asientos", response_model=list[AsientoOut])
async def list_asientos(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.get_asientos_by_bus(db, id_bus)


@router.get("/asientos/{id_asiento}", response_model=AsientoOut)
async def get_asiento(id_asiento: int, db: DbDep, _: AdminOrSuper):
    return await service.get_asiento_by_id(db, id_asiento)


@router.post("/asientos", response_model=AsientoOut, status_code=201)
async def create_asiento(body: AsientoCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_asiento(db, body)


@router.put("/asientos/{id_asiento}", response_model=AsientoOut)
async def update_asiento(id_asiento: int, body: AsientoUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_asiento(db, id_asiento, body)


@router.delete("/asientos/{id_asiento}")
async def delete_asiento(id_asiento: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_asiento(db, id_asiento)


# ── Amenidades ────────────────────────────────────────────────────────────────

@router.get("/buses/{id_bus}/amenidades", response_model=list[AmenidadOut])
async def list_amenidades(id_bus: int, db: DbDep, _: AdminOrSuper):
    return await service.get_amenidades_by_bus(db, id_bus)


@router.put("/buses/{id_bus}/amenidades", response_model=list[AmenidadOut])
async def replace_amenidades(id_bus: int, body: ReemplazarAmenidadesRequest, db: DbDep, _: AdminOrSuper):
    return await service.replace_amenidades(db, id_bus, body.amenidades)
