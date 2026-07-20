from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import (
    AdminOrSuperOrTerminal,
    DbDep,
    resolve_agencia_scope,
    resolve_terminal_scope,
)
from app.modules.manifiestos import service
from app.modules.manifiestos.schemas import ManifiestoDetalleOut, ManifiestoSutranOut

router = APIRouter(prefix="/admin/manifiestos", tags=["Manifiestos"])


@router.get("/", response_model=list[ManifiestoSutranOut])
async def list_manifiestos(
    db: DbDep,
    current_user: AdminOrSuperOrTerminal,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_all(db, skip, limit, id_agencia, id_terminal)


@router.get("/{id_manifiesto}", response_model=ManifiestoDetalleOut)
async def get_manifiesto(id_manifiesto: int, db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    result = await service.get_by_id(db, id_manifiesto, id_agencia, id_terminal)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manifiesto no encontrado")
    return result
