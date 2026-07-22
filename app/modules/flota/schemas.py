import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Placa peruana: 3 letras/dígitos, guion, 3 o 4 letras/dígitos (p.ej. CGS-103, A1B-2345).
PLACA_PATTERN = re.compile(r"^[A-Z0-9]{3}-[A-Z0-9]{3,4}$")


def validar_formato_placa(value: str) -> str:
    normalizada = value.strip().upper()
    if not PLACA_PATTERN.match(normalizada):
        raise ValueError(
            "Formato de placa inválido. Debe ser como CGS-103 (3 caracteres, guion, 3 o 4 caracteres)."
        )
    return normalizada


# ── Bus ──────────────────────────────────────────────────────────────────────

class BusBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    placa: str
    cantidad_pisos: int = Field(default=1, alias="cantidadPisos")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("placa")
    @classmethod
    def _validar_placa(cls, v: str) -> str:
        return validar_formato_placa(v)


class BusCreate(BusBase):
    pass


class BusUpdate(BaseModel):
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    placa: Optional[str] = None
    cantidad_pisos: Optional[int] = Field(default=None, alias="cantidadPisos")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("placa")
    @classmethod
    def _validar_placa(cls, v: Optional[str]) -> Optional[str]:
        return validar_formato_placa(v) if v is not None else v


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
