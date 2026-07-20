from fastapi import APIRouter, Query

from app.dependencies import AdminOrSuper, DbDep
from app.modules.usuarios import service
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioCreatedOut, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/admin/usuarios", tags=["Usuarios"])


@router.get("/", response_model=list[UsuarioOut])
async def list_usuarios(
    db: DbDep,
    current_user: AdminOrSuper,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_agencia: int | None = Query(default=None),
):
    return await service.list_usuarios(db, current_user, skip, limit, id_agencia)


@router.post("/", response_model=UsuarioCreatedOut, status_code=201)
async def create_usuario(body: UsuarioCreate, db: DbDep, current_user: AdminOrSuper):
    usuario, temp_password = await service.create_usuario(db, current_user, body)
    return UsuarioCreatedOut(
        idUsuario=usuario.id_usuario,
        email=usuario.email,
        telefono=usuario.telefono,
        rol=usuario.rol.value,
        idAgencia=usuario.id_agencia,
        idTerminal=usuario.id_terminal,
        activo=usuario.activo,
        fechaCreacion=usuario.fecha_creacion,
        passwordTemporal=temp_password,
    )


@router.put("/{id_usuario}", response_model=UsuarioOut)
async def update_usuario(id_usuario: int, body: UsuarioUpdate, db: DbDep, current_user: AdminOrSuper):
    return await service.update_usuario(db, current_user, id_usuario, body)


@router.delete("/{id_usuario}")
async def deactivate_usuario(id_usuario: int, db: DbDep, current_user: AdminOrSuper):
    return await service.deactivate_usuario(db, current_user, id_usuario)
