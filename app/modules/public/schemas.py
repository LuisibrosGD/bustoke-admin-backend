from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AsientoDisponibleOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_asiento")
    numero_asiento: str = Field(alias="numeroAsiento")
    fila: str
    piso: int
    tipo_servicio: str = Field(alias="tipoServicio")
    ocupado: bool
    bloqueado: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PasajeroCreate(BaseModel):
    id_tipo_documento: int = Field(alias="idTipoDocumento")
    numero_documento: str = Field(alias="numeroDocumento")
    nombres: str
    apellido_paterno: str = Field(alias="apellidoPaterno")
    apellido_materno: str = Field(alias="apellidoMaterno")
    fecha_nacimiento: Optional[date] = Field(default=None, alias="fechaNacimiento")


class BoletoExternoCreate(BaseModel):
    id_viaje: int = Field(alias="idViaje")
    id_asiento: int = Field(alias="idAsiento")
    email_contacto: str = Field(alias="emailContacto")
    precio_final: Decimal = Field(alias="precioFinal")
    pasajero: PasajeroCreate


class BoletoExternoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_boleto")
    id_viaje: int = Field(alias="idViaje")
    id_asiento: int = Field(alias="idAsiento")
    email_contacto: str = Field(alias="emailContacto")
    codigo_qr: str = Field(alias="codigoQr")
    precio_final: Decimal = Field(alias="precioFinal")
    fecha_emision: datetime = Field(alias="fechaEmision")
    estado: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
