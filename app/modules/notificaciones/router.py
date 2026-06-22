from fastapi import APIRouter, Depends, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.notificaciones import service
from app.modules.notificaciones.schemas import NotificacionOut, NotificacionUpdate

router = APIRouter(prefix="/admin/notificaciones", tags=["Notificaciones"])


@router.get("/", response_model=list[NotificacionOut])
async def list_notificaciones(
    db: DbDep,
    usuario: AdminOrSuper,
    solo_no_leidas: bool = Query(False, alias="soloNoLeidas"),
):
    return await service.get_notificaciones_by_usuario(
        db, int(usuario["sub"]), solo_no_leidas=solo_no_leidas
    )


@router.get("/contar")
async def contar_no_leidas(db: DbDep, usuario: AdminOrSuper):
    total = await service.contar_no_leidas(db, int(usuario["sub"]))
    return {"total": total}


@router.put("/{id_notificacion}", response_model=NotificacionOut)
async def marcar_leida(
    id_notificacion: int, body: NotificacionUpdate, db: DbDep, usuario: AdminOrSuper
):
    return await service.marcar_como_leida(db, id_notificacion, int(usuario["sub"]))


@router.put("/leer-todas")
async def marcar_todas_leidas(db: DbDep, usuario: AdminOrSuper):
    total = await service.marcar_todas_leidas(db, int(usuario["sub"]))
    return {"marcadas": total}
