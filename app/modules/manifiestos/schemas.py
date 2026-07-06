from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ManifiestoSutranOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_manifiesto")
    id_viaje: int = Field(alias="idViaje")
    fecha_generacion: datetime = Field(alias="fechaGeneracion")
    estado_envio: str = Field(alias="estadoEnvio")
    respuesta_api: str = Field(alias="respuestaApi")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ManifiestoDetalleOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_manifiesto")
    id_viaje: int = Field(alias="idViaje")
    fecha_generacion: datetime = Field(alias="fechaGeneracion")
    estado_envio: str = Field(alias="estadoEnvio")
    respuesta_api: str = Field(alias="respuestaApi")
    fecha_hora_salida: Optional[datetime] = Field(default=None, alias="fechaHoraSalida")
    fecha_hora_llegada: Optional[datetime] = Field(default=None, alias="fechaHoraLlegada")
    viaje_estado: Optional[str] = Field(default=None, alias="viajeEstado")
    rampa_embarque: Optional[str] = Field(default=None, alias="rampaEmbarque")
    placa_bus: Optional[str] = Field(default=None, alias="placaBus")
    ruta_origen: Optional[str] = Field(default=None, alias="rutaOrigen")
    ruta_destino: Optional[str] = Field(default=None, alias="rutaDestino")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
