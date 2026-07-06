from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import AdminOrSuper, DbDep
from app.modules.manifiestos import service
from app.modules.manifiestos.schemas import ManifiestoDetalleOut, ManifiestoSutranOut

router = APIRouter(prefix="/admin/manifiestos", tags=["Manifiestos"])


@router.get("/", response_model=list[ManifiestoSutranOut])
async def list_manifiestos(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    return await service.get_all(db, skip, limit)


@router.get("/{id_manifiesto}", response_model=ManifiestoDetalleOut)
async def get_manifiesto(id_manifiesto: int, db: DbDep, _: AdminOrSuper):
    result = await service.get_by_id(db, id_manifiesto)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manifiesto no encontrado")
    return result
