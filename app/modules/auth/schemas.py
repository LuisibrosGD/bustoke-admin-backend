from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    rol: str
    id_usuario: int = Field(alias="idUsuario")
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken")

    model_config = ConfigDict(populate_by_name=True)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(alias="newPassword")

    model_config = ConfigDict(populate_by_name=True)


class RecoverEmailRequest(BaseModel):
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(alias="oldPassword")
    new_password: str = Field(alias="newPassword")

    model_config = ConfigDict(populate_by_name=True)


class UserOut(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    email: str
    rol: str
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    activo: bool
    fecha_creacion: datetime = Field(alias="fechaCreacion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
