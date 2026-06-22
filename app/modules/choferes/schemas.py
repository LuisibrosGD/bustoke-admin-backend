from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChoferBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    id_tipo_documento: int = Field(alias="idTipoDocumento")
    numero_documento: str = Field(alias="numeroDocumento")
    nombres: str
    apellido_paterno: str = Field(alias="apellidoPaterno")
    apellido_materno: str = Field(alias="apellidoMaterno")
    activo: bool = True

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ChoferCreate(ChoferBase):
    pass


class ChoferUpdate(BaseModel):
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    id_tipo_documento: Optional[int] = Field(default=None, alias="idTipoDocumento")
    numero_documento: Optional[str] = Field(default=None, alias="numeroDocumento")
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = Field(default=None, alias="apellidoPaterno")
    apellido_materno: Optional[str] = Field(default=None, alias="apellidoMaterno")
    activo: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ChoferOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_chofer")
    id_agencia: int = Field(alias="idAgencia")
    id_tipo_documento: int = Field(alias="idTipoDocumento")
    numero_documento: str = Field(alias="numeroDocumento")
    nombres: str
    apellido_paterno: str = Field(alias="apellidoPaterno")
    apellido_materno: str = Field(alias="apellidoMaterno")
    activo: bool
    fecha_registro: datetime = Field(alias="fechaRegistro")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
