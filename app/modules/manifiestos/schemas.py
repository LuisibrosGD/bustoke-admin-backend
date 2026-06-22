from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ManifiestoSutranOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_manifiesto")
    id_viaje: int = Field(alias="idViaje")
    fecha_generacion: datetime = Field(alias="fechaGeneracion")
    estado_envio: str = Field(alias="estadoEnvio")
    respuesta_api: str = Field(alias="respuestaApi")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
