from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.modules.auth.models import Usuario


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException("Credenciales incorrectas")
    if not user.activo:
        raise UnauthorizedException("Usuario inactivo")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedException("Credenciales incorrectas")
    return user


def build_token_response(user: Usuario) -> dict:
    payload = {
        "sub": str(user.id_usuario),
        "email": user.email,
        "rol": user.rol.value,
        "id_agencia": user.id_agencia,
        "id_terminal": user.id_terminal,
    }
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "bearer",
        "rol": user.rol.value,
        "idUsuario": user.id_usuario,
        "idAgencia": user.id_agencia,
        "idTerminal": user.id_terminal,
    }


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise UnauthorizedException("Refresh token inválido o expirado")
    if payload.get("type") != "refresh":
        raise UnauthorizedException("Token de tipo incorrecto")
    user_id = int(payload.get("sub", 0))
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.activo:
        raise UnauthorizedException("Usuario no encontrado o inactivo")
    return build_token_response(user)


async def get_usuario(db: AsyncSession, id_usuario: int) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == id_usuario))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException(f"Usuario {id_usuario} no encontrado")
    return user


async def forgot_password(db: AsyncSession, email: str) -> dict:
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one_or_none()
    # No revelamos si el correo existe o no
    if user:
        payload = {
            "sub": str(user.id_usuario),
            "email": user.email,
            "type": "password_reset",
        }
        reset_token = create_access_token(payload, expires_delta=timedelta(hours=1))
        # TODO: Integrar servicio de emails (SMTP/SendGrid) para enviar:
        # f"Para restablecer tu contraseña, usa este enlace: http://localhost:3000/admin/auth/reset-password?token={reset_token}"
    return {"message": "Si el correo existe, recibirás instrucciones de recuperación"}


async def reset_password(db: AsyncSession, token: str, new_password: str) -> dict:
    try:
        payload = decode_token(token)
    except ValueError:
        raise BadRequestException("Token de restablecimiento inválido o expirado")
    user_id = int(payload.get("sub", 0))
    result = await db.execute(select(Usuario).where(Usuario.id_usuario == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("Usuario no encontrado")
    user.password_hash = get_password_hash(new_password)
    await db.commit()
    return {"message": "Contraseña restablecida correctamente"}


async def recover_email(db: AsyncSession, email: str) -> dict:
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one_or_none()
    return {"message": "Si el correo existe, recibirás un enlace de recuperación"}
