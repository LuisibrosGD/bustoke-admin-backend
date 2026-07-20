from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database import get_db
from app.modules.finanzas.service import get_api_key_by_token
from app.modules.rutas.models import Ruta

security = HTTPBearer()


async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException("Token de tipo incorrecto")
        return payload
    except ValueError:
        raise UnauthorizedException("Token inválido o expirado")


async def require_superadmin(
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> dict:
    if payload.get("rol") != "superadmin":
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Se requiere rol superadmin")
    return payload


async def require_admin_or_superadmin(
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> dict:
    if payload.get("rol") not in ("admin_agencia", "superadmin"):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Se requiere rol admin_agencia o superadmin")
    return payload


async def require_admin_or_superadmin_or_terminal(
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> dict:
    if payload.get("rol") not in ("admin_agencia", "superadmin", "admin_terminal"):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Se requiere rol admin_agencia, admin_terminal o superadmin")
    return payload


DbDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user_payload)]
SuperAdmin = Annotated[dict, Depends(require_superadmin)]
AdminOrSuper = Annotated[dict, Depends(require_admin_or_superadmin)]
AdminOrSuperOrTerminal = Annotated[dict, Depends(require_admin_or_superadmin_or_terminal)]


def resolve_agencia_scope(current_user: dict, id_agencia: int | None = None) -> int | None:
    """Calcula el id_agencia efectivo para filtrar una consulta.

    Un admin_agencia o admin_terminal SIEMPRE queda restringido a su propia
    agencia, sin importar qué id_agencia haya mandado el cliente en la query
    (evita que pida datos de otra agencia pasando el parámetro). Un
    superadmin puede filtrar libremente (o ver todo si no manda nada).

    IMPORTANTE: admin_terminal debe incluirse aquí además de en
    resolve_terminal_scope. Si un endpoint solo llama a esta función (sin
    también aplicar resolve_terminal_scope), un admin_terminal que no
    calzara en este `if` quedaría sin ninguna restricción de agencia.
    """
    user_rol = current_user.get("rol")
    user_agencia = current_user.get("id_agencia")
    if user_rol in ("admin_agencia", "admin_terminal") and user_agencia:
        return user_agencia
    return id_agencia


def resolve_terminal_scope(current_user: dict, id_terminal: int | None = None) -> int | None:
    """Calcula el id_terminal efectivo para filtrar una consulta.

    Análogo a resolve_agencia_scope: un admin_terminal SIEMPRE queda
    restringido a su propio terminal, sin importar qué id_terminal mande
    el cliente. Los demás roles no tienen restricción de terminal (pueden
    ver todos los terminales de su agencia, o de todas si son superadmin).
    """
    user_rol = current_user.get("rol")
    user_terminal = current_user.get("id_terminal")
    if user_rol == "admin_terminal" and user_terminal:
        return user_terminal
    return id_terminal


def terminal_ruta_condition(id_terminal: int):
    """Condición de scope por terminal, compartida por todos los módulos
    que filtran vía Ruta: un terminal puede ser origen O destino."""
    return or_(Ruta.id_terminal_origen == id_terminal, Ruta.id_terminal_destino == id_terminal)


async def require_api_key(
    db: DbDep,
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
) -> dict:
    if not x_api_key:
        raise UnauthorizedException("API Key requerida (header x-api-key)")
    key = await get_api_key_by_token(db, x_api_key)
    if not key:
        raise UnauthorizedException("API Key inválida o expirada")
    return {"id_agencia": key.id_agencia, "id_api_key": key.id_api_key}


ApiKeyAuth = Annotated[dict, Depends(require_api_key)]
