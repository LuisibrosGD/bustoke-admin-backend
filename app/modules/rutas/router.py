from datetime import datetime

from fastapi import APIRouter, File, Query, Response, UploadFile

from app.core.exceptions import BadRequestException, ForbiddenException
from app.core.excel import export_excel, read_excel_rows
from app.dependencies import (
    AdminOrSuper,
    AdminOrSuperOrTerminal,
    DbDep,
    resolve_agencia_scope,
    resolve_terminal_scope,
)
from app.modules.rutas import service
from app.modules.rutas.schemas import (
    RutaCreate,
    RutaOut,
    RutaUpdate,
    TarifaRutaCreate,
    TarifaRutaOut,
    TarifaRutaUpdate,
)

router = APIRouter(prefix="/admin/rutas", tags=["Rutas"])


# ── Rutas ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[RutaOut])
async def list_rutas(
    db: DbDep,
    current_user: AdminOrSuperOrTerminal,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    id_terminal = resolve_terminal_scope(current_user)
    if id_terminal:
        return await service.get_rutas_scoped(db, id_agencia, id_terminal)
    if id_agencia:
        return await service.get_rutas_by_agencia(db, id_agencia)
    return await service.get_all_rutas(db, skip, limit)


@router.get("/{id_ruta}", response_model=RutaOut)
async def get_ruta(id_ruta: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    ruta = await service.get_ruta_by_id(db, id_ruta)
    scoped_terminal = resolve_terminal_scope(current_user)
    if scoped_terminal and scoped_terminal not in (ruta.id_terminal_origen, ruta.id_terminal_destino):
        raise ForbiddenException("No tienes acceso a esta ruta")
    return ruta


@router.post("/", response_model=RutaOut, status_code=201)
async def create_ruta(body: RutaCreate, db: DbDep, current_user: AdminOrSuper):
    body.id_agencia = resolve_agencia_scope(current_user, body.id_agencia)
    return await service.create_ruta(db, body)


@router.put("/{id_ruta}", response_model=RutaOut)
async def update_ruta(id_ruta: int, body: RutaUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_ruta(db, id_ruta, body)


@router.post("/carga-masiva")
async def bulk_upload_rutas(
    db: DbDep,
    current_user: AdminOrSuper,
    file: UploadFile = File(...),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    if not id_agencia:
        raise BadRequestException("Selecciona una agencia para la carga masiva")
    rows = read_excel_rows(await file.read())
    result = await service.bulk_create_rutas(db, id_agencia, rows)
    result["file"] = {
        "resourceId": "",
        "originalName": file.filename,
        "uploadedBy": current_user.get("email", ""),
        "uploadedAt": datetime.now().isoformat(),
    }
    return result


@router.get("/carga-masiva/plantilla")
async def descargar_plantilla_rutas(_: AdminOrSuper):
    data = [{"Terminal Origen": "Terminal Terrestre Plaza Norte", "Terminal Destino": "Terminal Terrestre de Trujillo", "Tarifa Base": "45.00"}]
    content = await export_excel(data, sheet_name="Rutas")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_rutas.xlsx"},
    )


@router.delete("/{id_ruta}")
async def delete_ruta(id_ruta: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_ruta(db, id_ruta)


# ── Tarifas ───────────────────────────────────────────────────────────────────

@router.get("/{id_ruta}/tarifas", response_model=list[TarifaRutaOut])
async def list_tarifas(id_ruta: int, db: DbDep, _: AdminOrSuper):
    return await service.get_tarifas_by_ruta(db, id_ruta)


@router.get("/tarifas/{id_tarifa}", response_model=TarifaRutaOut)
async def get_tarifa(id_tarifa: int, db: DbDep, _: AdminOrSuper):
    return await service.get_tarifa_by_id(db, id_tarifa)


@router.post("/tarifas", response_model=TarifaRutaOut, status_code=201)
async def create_tarifa(body: TarifaRutaCreate, db: DbDep, _: AdminOrSuper):
    return await service.create_tarifa(db, body)


@router.put("/tarifas/{id_tarifa}", response_model=TarifaRutaOut)
async def update_tarifa(id_tarifa: int, body: TarifaRutaUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update_tarifa(db, id_tarifa, body)


@router.delete("/tarifas/{id_tarifa}")
async def delete_tarifa(id_tarifa: int, db: DbDep, _: AdminOrSuper):
    return await service.delete_tarifa(db, id_tarifa)
