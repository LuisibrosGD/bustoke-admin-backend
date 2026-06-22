from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.manifiestos import service
from app.modules.manifiestos.schemas import ManifiestoSutranOut

router = APIRouter(prefix="/admin/manifiestos", tags=["Manifiestos"])


@router.get("/", response_model=list[ManifiestoSutranOut])
async def list_manifiestos(
    db: DbDep,
    _: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    return await service.get_all(db, skip, limit)
