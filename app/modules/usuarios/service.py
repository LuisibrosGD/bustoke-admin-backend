import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.core.security import get_password_hash
from app.modules.agencias_terminales.models import AgenciaTerminal
from app.modules.auth.models import RolUsuario, Usuario
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioUpdate


def _generate_temp_password() -> str:
    return secrets.token_urlsafe(9)


async def _terminal_pertenece_a_agencia(db: AsyncSession, id_agencia: int, id_terminal: int) -> bool:
    result = await db.execute(
        select(AgenciaTerminal).where(
            AgenciaTerminal.id_agencia == id_agencia,
            AgenciaTerminal.id_terminal == id_terminal,
        )
    )
    return result.scalar_one_or_none() is not None


async def list_usuarios(
    db: AsyncSession,
    current_user: dict,
    skip: int = 0,
    limit: int = 100,
    id_agencia: int | None = None,
) -> list[Usuario]:
    # admin_agencia solo ve usuarios de su propia agencia, sin importar qué
    # id_agencia mande en la query (mismo patrón que resolve_agencia_scope).
    if current_user.get("rol") == "admin_agencia":
        id_agencia = current_user.get("id_agencia")

    query = select(Usuario).where(Usuario.rol != RolUsuario.cliente)
    if id_agencia:
        query = query.where(Usuario.id_agencia == id_agencia)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_usuario(db: AsyncSession, current_user: dict, data: UsuarioCreate) -> tuple[Usuario, str]:
    creador_rol = current_user.get("rol")
    creador_agencia = current_user.get("id_agencia")

    if creador_rol == "admin_agencia":
        # Un admin_agencia solo puede crear encargados de terminal (nunca
        # otro admin_agencia ni superadmin) y siempre dentro de SU agencia,
        # sin importar qué id_agencia mande el body.
        if data.rol != RolUsuario.admin_terminal:
            raise ForbiddenException(
                "Un admin_agencia solo puede crear usuarios con rol admin_terminal"
            )
        id_agencia = creador_agencia
    elif creador_rol == "superadmin":
        if data.rol == RolUsuario.cliente:
            raise BadRequestException("Este módulo no gestiona usuarios tipo cliente")
        id_agencia = data.id_agencia
    else:
        raise ForbiddenException("No tienes permiso para crear usuarios")

    id_terminal = data.id_terminal
    if data.rol == RolUsuario.admin_terminal:
        if not id_agencia:
            raise BadRequestException("admin_terminal requiere una agencia")
        if not id_terminal:
            raise BadRequestException("admin_terminal requiere un terminal")
        if not await _terminal_pertenece_a_agencia(db, id_agencia, id_terminal):
            raise BadRequestException("El terminal indicado no pertenece a la agencia")
    else:
        id_terminal = None
        if data.rol == RolUsuario.admin_agencia and not id_agencia:
            raise BadRequestException("admin_agencia requiere una agencia")

    existing = await db.execute(select(Usuario).where(Usuario.email == data.email))
    if existing.scalar_one_or_none():
        raise BadRequestException("Ya existe un usuario con ese correo")

    temp_password = data.password_temporal or _generate_temp_password()
    usuario = Usuario(
        email=data.email,
        telefono=data.telefono,
        password_hash=get_password_hash(temp_password),
        rol=data.rol,
        id_agencia=id_agencia,
        id_terminal=id_terminal,
        activo=True,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario, temp_password


async def update_usuario(db: AsyncSession, current_user: dict, id_usuario: int, data: UsuarioUpdate) -> Usuario:
    usuario = await _get_usuario_editable(db, current_user, id_usuario)

    if data.telefono is not None:
        usuario.telefono = data.telefono
    if data.activo is not None:
        usuario.activo = data.activo
    if data.id_terminal is not None:
        if usuario.rol != RolUsuario.admin_terminal:
            raise BadRequestException("Solo un usuario admin_terminal puede tener id_terminal")
        if not usuario.id_agencia or not await _terminal_pertenece_a_agencia(
            db, usuario.id_agencia, data.id_terminal
        ):
            raise BadRequestException("El terminal indicado no pertenece a la agencia del usuario")
        usuario.id_terminal = data.id_terminal

    await db.commit()
    await db.refresh(usuario)
    return usuario


async def deactivate_usuario(db: AsyncSession, current_user: dict, id_usuario: int) -> dict:
    usuario = await _get_usuario_editable(db, current_user, id_usuario)
    usuario.activo = False
    await db.commit()
    return {"message": "Usuario desactivado correctamente"}


async def _get_usuario_editable(db: AsyncSession, current_user: dict, id_usuario: int) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == id_usuario))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise NotFoundException(f"Usuario {id_usuario} no encontrado")

    creador_rol = current_user.get("rol")
    if creador_rol == "admin_agencia":
        if usuario.id_agencia != current_user.get("id_agencia") or usuario.rol != RolUsuario.admin_terminal:
            raise ForbiddenException("No tienes permiso para editar este usuario")
    elif creador_rol != "superadmin":
        raise ForbiddenException("No tienes permiso para editar usuarios")

    return usuario
