from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReporteVentasRow(BaseModel):
    periodo: str
    total_boletos: int = Field(alias="totalBoletos")
    total_ventas: float = Field(alias="totalVentas")
    canal: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReporteViajesRow(BaseModel):
    id_viaje: int = Field(alias="idViaje")
    ruta: str
    fecha_salida: str = Field(alias="fechaSalida")
    estado: str
    total_boletos: int = Field(alias="totalBoletos")
    ocupacion: float

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReporteManifiestoRow(BaseModel):
    id_viaje: int = Field(alias="idViaje")
    pasajero: str
    numero_documento: str = Field(alias="numeroDocumento")
    asiento: str
    email_contacto: str = Field(alias="emailContacto")
    precio_final: float = Field(alias="precioFinal")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReporteGenericoOut(BaseModel):
    slug: str
    data: list[dict[str, Any]]
    total: int
    page: int
    limit: int
    total_pages: int = Field(alias="totalPages")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
