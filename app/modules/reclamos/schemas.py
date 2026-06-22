from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MensajeReclamoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_mensaje")
    id_reclamo: int = Field(alias="idReclamo")
    id_usuario: int = Field(alias="idUsuario")
    text_mensaje: str = Field(alias="textMensaje")
    fecha: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MensajeReclamoCreate(BaseModel):
    id_reclamo: int = Field(alias="idReclamo")
    id_usuario: int = Field(alias="idUsuario")
    text_mensaje: str = Field(alias="textMensaje")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReclamoBase(BaseModel):
    id_usuario: int = Field(alias="idUsuario")
    id_agencia: int = Field(alias="idAgencia")
    motivo: str
    detalle: str
    estado: str = "abierto"

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReclamoCreate(ReclamoBase):
    pass


class ReclamoUpdate(BaseModel):
    motivo: Optional[str] = None
    detalle: Optional[str] = None
    estado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReclamoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_reclamo")
    id_usuario: int = Field(alias="idUsuario")
    id_agencia: int = Field(alias="idAgencia")
    motivo: str
    detalle: str
    estado: str
    fecha_creacion: datetime = Field(alias="fechaCreacion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
