from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database import get_db
from app.modules.finanzas.service import get_api_key_by_token

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


DbDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user_payload)]
SuperAdmin = Annotated[dict, Depends(require_superadmin)]
AdminOrSuper = Annotated[dict, Depends(require_admin_or_superadmin)]


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
