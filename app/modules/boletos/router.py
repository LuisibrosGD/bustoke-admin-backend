from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.viajes import service as viajes_service
from app.modules.viajes.schemas import BoletoCreate, BoletoOut, BoletoUpdate

router = APIRouter(prefix="/admin/boletos", tags=["Boletos"])


@router.get("/", response_model=list[BoletoOut])
async def list_boletos(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = None,
):
    user_agencia = current_user.get("id_agencia")
    user_rol = current_user.get("rol")
    if not id_agencia and user_rol == "admin_agencia" and user_agencia:
        id_agencia = user_agencia
    if id_agencia:
        return await viajes_service.get_boletos_by_agencia(db, id_agencia, skip, limit)
    return await viajes_service.get_all_boletos(db, skip, limit)


@router.get("/{id_boleto}", response_model=BoletoOut)
async def get_boleto(id_boleto: int, db: DbDep, _: AdminOrSuper):
    return await viajes_service.get_boleto_by_id(db, id_boleto)


@router.post("/", response_model=BoletoOut, status_code=201)
async def create_boleto(body: BoletoCreate, db: DbDep, _: AdminOrSuper):
    return await viajes_service.create_boleto(db, body)


@router.put("/{id_boleto}", response_model=BoletoOut)
async def update_boleto(id_boleto: int, body: BoletoUpdate, db: DbDep, _: AdminOrSuper):
    return await viajes_service.update_boleto(db, id_boleto, body)


@router.delete("/{id_boleto}")
async def delete_boleto(id_boleto: int, db: DbDep, _: AdminOrSuper):
    return await viajes_service.delete_boleto(db, id_boleto)
