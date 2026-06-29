from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Viaje ─────────────────────────────────────────────────────────────────────

class ViajeBase(BaseModel):
    id_ruta: int = Field(alias="idRuta")
    id_bus: int = Field(alias="idBus")
    id_chofer: Optional[int] = Field(default=None, alias="idChofer")
    fecha_hora_salida: datetime = Field(alias="fechaHoraSalida")
    fecha_hora_llegada: datetime = Field(alias="fechaHoraLlegada")
    estado: str = "programado"
    rampa_embarque: str = Field(default="Por asignar", alias="rampaEmbarque")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ViajeCreate(ViajeBase):
    pass


class ViajeUpdate(BaseModel):
    id_ruta: Optional[int] = Field(default=None, alias="idRuta")
    id_bus: Optional[int] = Field(default=None, alias="idBus")
    id_chofer: Optional[int] = Field(default=None, alias="idChofer")
    fecha_hora_salida: Optional[datetime] = Field(default=None, alias="fechaHoraSalida")
    fecha_hora_llegada: Optional[datetime] = Field(default=None, alias="fechaHoraLlegada")
    estado: Optional[str] = None
    rampa_embarque: Optional[str] = Field(default=None, alias="rampaEmbarque")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ViajeOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_viaje")
    id_ruta: int = Field(alias="idRuta")
    id_bus: int = Field(alias="idBus")
    id_chofer: Optional[int] = Field(default=None, alias="idChofer")
    fecha_hora_salida: datetime = Field(alias="fechaHoraSalida")
    fecha_hora_llegada: datetime = Field(alias="fechaHoraLlegada")
    estado: str
    rampa_embarque: str = Field(alias="rampaEmbarque")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Pasajero ──────────────────────────────────────────────────────────────────

class PasajeroBase(BaseModel):
    id_usuario: Optional[int] = Field(default=None, alias="idUsuario")
    id_tipo_documento: int = Field(alias="idTipoDocumento")
    numero_documento: str = Field(alias="numeroDocumento")
    nombres: str
    apellido_paterno: str = Field(alias="apellidoPaterno")
    apellido_materno: str = Field(alias="apellidoMaterno")
    fecha_nacimiento: Optional[date] = Field(default=None, alias="fechaNacimiento")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PasajeroCreate(PasajeroBase):
    pass


class PasajeroUpdate(BaseModel):
    id_tipo_documento: Optional[int] = Field(default=None, alias="idTipoDocumento")
    numero_documento: Optional[str] = Field(default=None, alias="numeroDocumento")
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = Field(default=None, alias="apellidoPaterno")
    apellido_materno: Optional[str] = Field(default=None, alias="apellidoMaterno")
    fecha_nacimiento: Optional[date] = Field(default=None, alias="fechaNacimiento")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PasajeroOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_pasajero")
    id_usuario: Optional[int] = Field(default=None, alias="idUsuario")
    id_tipo_documento: int = Field(alias="idTipoDocumento")
    numero_documento: str = Field(alias="numeroDocumento")
    nombres: str
    apellido_paterno: str = Field(alias="apellidoPaterno")
    apellido_materno: str = Field(alias="apellidoMaterno")
    fecha_nacimiento: Optional[date] = Field(default=None, alias="fechaNacimiento")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Boleto ────────────────────────────────────────────────────────────────────

class BoletoBase(BaseModel):
    id_viaje: int = Field(alias="idViaje")
    id_usuario: Optional[int] = Field(default=None, alias="idUsuario")
    id_pasajero: int = Field(alias="idPasajero")
    id_asiento: int = Field(alias="idAsiento")
    email_contacto: str = Field(alias="emailContacto")
    canal: str
    codigo_qr: str = Field(alias="codigoQr")
    precio_final: Decimal = Field(alias="precioFinal")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BoletoCreate(BoletoBase):
    pass


class BoletoUpdate(BaseModel):
    estado: Optional[str] = None
    usado: Optional[bool] = None
    fecha_validacion: Optional[datetime] = Field(default=None, alias="fechaValidacion")
    estado_checkin: Optional[str] = Field(default=None, alias="estadoCheckin")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BoletoCheckIn(BaseModel):
    estado_checkin: str = Field(alias="estadoCheckin")

    model_config = ConfigDict(populate_by_name=True)


class BoletoScanRequest(BaseModel):
    codigo_qr: str = Field(alias="codigoQr")

    model_config = ConfigDict(populate_by_name=True)


class BoletoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_boleto")
    id_viaje: int = Field(alias="idViaje")
    id_usuario: Optional[int] = Field(default=None, alias="idUsuario")
    id_pasajero: int = Field(alias="idPasajero")
    id_asiento: int = Field(alias="idAsiento")
    email_contacto: str = Field(alias="emailContacto")
    canal: str
    codigo_qr: str = Field(alias="codigoQr")
    usado: bool
    fecha_validacion: Optional[datetime] = Field(default=None, alias="fechaValidacion")
    precio_final: Decimal = Field(alias="precioFinal")
    fecha_emision: datetime = Field(alias="fechaEmision")
    estado: str
    estado_checkin: str = Field(alias="estadoCheckin")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
