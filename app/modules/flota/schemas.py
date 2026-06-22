from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Bus ──────────────────────────────────────────────────────────────────────

class BusBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    placa: str
    cantidad_pisos: int = Field(default=1, alias="cantidadPisos")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BusCreate(BusBase):
    pass


class BusUpdate(BaseModel):
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    placa: Optional[str] = None
    cantidad_pisos: Optional[int] = Field(default=None, alias="cantidadPisos")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BusOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_bus")
    id_agencia: int = Field(alias="idAgencia")
    placa: str
    cantidad_pisos: int = Field(alias="cantidadPisos")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Asiento ───────────────────────────────────────────────────────────────────

class AsientoBase(BaseModel):
    id_bus: int = Field(alias="idBus")
    numero_asiento: str = Field(alias="numeroAsiento")
    fila: str
    piso: int = 1
    tipo_servicio: str = Field(default="normal", alias="tipoServicio")
    coord_x: int = Field(alias="coordX")
    coord_y: int = Field(alias="coordY")
    bloqueado_manual: bool = Field(default=False, alias="bloqueadoManual")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AsientoCreate(AsientoBase):
    pass


class AsientoUpdate(BaseModel):
    id_bus: Optional[int] = Field(default=None, alias="idBus")
    numero_asiento: Optional[str] = Field(default=None, alias="numeroAsiento")
    fila: Optional[str] = None
    piso: Optional[int] = None
    tipo_servicio: Optional[str] = Field(default=None, alias="tipoServicio")
    coord_x: Optional[int] = Field(default=None, alias="coordX")
    coord_y: Optional[int] = Field(default=None, alias="coordY")
    bloqueado_manual: Optional[bool] = Field(default=None, alias="bloqueadoManual")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AsientoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_asiento")
    id_bus: int = Field(alias="idBus")
    numero_asiento: str = Field(alias="numeroAsiento")
    fila: str
    piso: int
    tipo_servicio: str = Field(alias="tipoServicio")
    coord_x: int = Field(alias="coordX")
    coord_y: int = Field(alias="coordY")
    bloqueado_manual: bool = Field(alias="bloqueadoManual")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
