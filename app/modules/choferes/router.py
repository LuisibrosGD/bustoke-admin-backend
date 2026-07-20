from datetime import datetime

from fastapi import APIRouter, File, Query, Response, UploadFile

from app.core.exceptions import BadRequestException
from app.core.excel import export_excel, read_excel_rows
from app.dependencies import AdminOrSuper, DbDep, resolve_agencia_scope
from app.modules.choferes import service
from app.modules.choferes.schemas import (
    ChoferCreate,
    ChoferOut,
    ChoferUpdate,
)

router = APIRouter(prefix="/admin/choferes", tags=["Choferes"])


@router.get("/", response_model=list[ChoferOut])
async def list_choferes(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    if id_agencia:
        return await service.get_by_agencia(db, id_agencia)
    return await service.get_all(db, skip, limit)


@router.get("/{id_chofer}", response_model=ChoferOut)
async def get_chofer(id_chofer: int, db: DbDep, _: AdminOrSuper):
    return await service.get_by_id(db, id_chofer)


@router.post("/", response_model=ChoferOut, status_code=201)
async def create_chofer(body: ChoferCreate, db: DbDep, current_user: AdminOrSuper):
    body.id_agencia = resolve_agencia_scope(current_user, body.id_agencia)
    return await service.create(db, body)


@router.put("/{id_chofer}", response_model=ChoferOut)
async def update_chofer(id_chofer: int, body: ChoferUpdate, db: DbDep, _: AdminOrSuper):
    return await service.update(db, id_chofer, body)


@router.post("/carga-masiva")
async def bulk_upload_choferes(
    db: DbDep,
    current_user: AdminOrSuper,
    file: UploadFile = File(...),
    id_agencia: int | None = None,
):
    id_agencia = resolve_agencia_scope(current_user, id_agencia)
    if not id_agencia:
        raise BadRequestException("Selecciona una agencia para la carga masiva")
    rows = read_excel_rows(await file.read())
    result = await service.bulk_create(db, id_agencia, rows)
    result["file"] = {
        "resourceId": "",
        "originalName": file.filename,
        "uploadedBy": current_user.get("email", ""),
        "uploadedAt": datetime.now().isoformat(),
    }
    return result


@router.get("/carga-masiva/plantilla")
async def descargar_plantilla_choferes(_: AdminOrSuper):
    data = [{"Tipo Documento": "DNI", "Número Documento": "12345678", "Nombres": "Juan", "Apellido Paterno": "Pérez", "Apellido Materno": "García"}]
    content = await export_excel(data, sheet_name="Choferes")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_choferes.xlsx"},
    )


@router.delete("/{id_chofer}")
async def delete_chofer(id_chofer: int, db: DbDep, _: AdminOrSuper):
    return await service.delete(db, id_chofer)
