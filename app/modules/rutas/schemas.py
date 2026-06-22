from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Ruta ─────────────────────────────────────────────────────────────────────

class RutaBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    id_terminal_origen: int = Field(alias="idTerminalOrigen")
    id_terminal_destino: int = Field(alias="idTerminalDestino")
    tarifa_base: Decimal = Field(alias="tarifaBase")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RutaCreate(RutaBase):
    pass


class RutaUpdate(BaseModel):
    id_agencia: Optional[int] = Field(default=None, alias="idAgencia")
    id_terminal_origen: Optional[int] = Field(default=None, alias="idTerminalOrigen")
    id_terminal_destino: Optional[int] = Field(default=None, alias="idTerminalDestino")
    tarifa_base: Optional[Decimal] = Field(default=None, alias="tarifaBase")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RutaOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_ruta")
    id_agencia: int = Field(alias="idAgencia")
    id_terminal_origen: int = Field(alias="idTerminalOrigen")
    id_terminal_destino: int = Field(alias="idTerminalDestino")
    tarifa_base: Decimal = Field(alias="tarifaBase")
    terminal_origen_nombre: str | None = Field(default=None, alias="terminalOrigenNombre")
    terminal_destino_nombre: str | None = Field(default=None, alias="terminalDestinoNombre")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── TarifaRuta ────────────────────────────────────────────────────────────────

class TarifaRutaBase(BaseModel):
    id_ruta: int = Field(alias="idRuta")
    tipo_servicio: str = Field(alias="tipoServicio")
    precio: Decimal

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TarifaRutaCreate(TarifaRutaBase):
    pass


class TarifaRutaUpdate(BaseModel):
    tipo_servicio: Optional[str] = Field(default=None, alias="tipoServicio")
    precio: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TarifaRutaOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_tarifa")
    id_ruta: int = Field(alias="idRuta")
    tipo_servicio: str = Field(alias="tipoServicio")
    precio: Decimal

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
