from fastapi import APIRouter

from app.dependencies import (
    AdminOrSuperOrTerminal,
    DbDep,
    resolve_agencia_scope,
    resolve_terminal_scope,
)
from app.modules.dashboard import service

router = APIRouter(prefix="/admin/dashboard", tags=["Dashboard"])


@router.get("/")
async def get_dashboard(db: DbDep, current_user: AdminOrSuperOrTerminal):
    id_agencia = resolve_agencia_scope(current_user)
    id_terminal = resolve_terminal_scope(current_user)
    return await service.get_dashboard_data(db, id_agencia, id_terminal)
