from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.auth.models import RolUsuario


class UsuarioCreate(BaseModel):
    email: EmailStr
    telefono: Optional[str] = None
    rol: RolUsuario
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    id_terminal: Optional[int] = Field(default=None, alias="idTerminal")
    # Si no se manda, el servicio genera una contraseña temporal aleatoria
    # y la devuelve una sola vez en la respuesta (ver UsuarioCreatedOut).
    password_temporal: Optional[str] = Field(default=None, alias="passwordTemporal")

    model_config = ConfigDict(populate_by_name=True)


class UsuarioUpdate(BaseModel):
    telefono: Optional[str] = None
    activo: Optional[bool] = None
    id_terminal: Optional[int] = Field(default=None, alias="idTerminal")

    model_config = ConfigDict(populate_by_name=True)


class UsuarioOut(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    email: str
    telefono: Optional[str] = None
    rol: str
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    id_terminal: Optional[int] = Field(default=None, alias="idTerminal")
    activo: bool
    fecha_creacion: datetime = Field(alias="fechaCreacion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UsuarioCreatedOut(UsuarioOut):
    password_temporal: str = Field(alias="passwordTemporal")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
