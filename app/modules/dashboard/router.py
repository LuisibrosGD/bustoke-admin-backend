from fastapi import APIRouter

from app.dependencies import AdminOrSuper, DbDep
from app.modules.dashboard import service

router = APIRouter(prefix="/admin/dashboard", tags=["Dashboard"])


@router.get("/")
async def get_dashboard(db: DbDep, current_user: AdminOrSuper):
    user_agencia = current_user.get("id_agencia")
    user_rol = current_user.get("rol")
    id_agencia = user_agencia if user_rol == "admin_agencia" else None
    return await service.get_dashboard_data(db, id_agencia)
