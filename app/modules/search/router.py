from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, resolve_agencia_scope
from app.modules.search import service

router = APIRouter(prefix="/admin/search", tags=["Búsqueda"])


@router.get("/")
async def search(current_user: AdminOrSuper, q: str = Query(..., min_length=2, max_length=100)):
    id_agencia = resolve_agencia_scope(current_user)
    is_superadmin = current_user.get("rol") == "superadmin"
    return await service.search(q, id_agencia, is_superadmin)
