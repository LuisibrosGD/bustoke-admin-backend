from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketSoporteBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    asunto: str
    descripcion: str
    estado: str = "abierto"

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TicketSoporteCreate(TicketSoporteBase):
    pass


class TicketSoporteUpdate(BaseModel):
    asunto: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TicketSoporteOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_ticket_soporte")
    id_agencia: int = Field(alias="idAgencia")
    asunto: str
    descripcion: str
    estado: str
    fecha_creacion: datetime = Field(alias="fechaCreacion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class HistorialCambioOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_historial")
    id_ticket: int = Field(alias="idTicket")
    campo: str
    valor_anterior: Optional[str] = Field(default=None, alias="valorAnterior")
    valor_nuevo: str = Field(alias="valorNuevo")
    id_usuario_modifica: Optional[int] = Field(default=None, alias="idUsuarioModifica")
    fecha_cambio: datetime = Field(alias="fechaCambio")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
