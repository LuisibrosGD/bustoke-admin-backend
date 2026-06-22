from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificacionOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_notificacion")
    id_usuario: int = Field(alias="idUsuario")
    tipo: str
    titulo: str
    mensaje: str
    referencia_tipo: Optional[str] = Field(default=None, alias="referenciaTipo")
    referencia_id: Optional[int] = Field(default=None, alias="referenciaId")
    leida: bool
    fecha_creacion: datetime = Field(alias="fechaCreacion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NotificacionUpdate(BaseModel):
    leida: bool

    model_config = ConfigDict(from_attributes=True)
