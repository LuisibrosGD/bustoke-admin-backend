from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Liquidacion ───────────────────────────────────────────────────────────────

class LiquidacionBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    periodo: str
    monto_ventas: Decimal = Field(alias="montoVentas")
    comision_plataforma: Decimal = Field(alias="comisionPlataforma")
    monto_a_transferir: Decimal = Field(alias="montoATransferir")
    estado_pago: str = Field(default="pendiente", alias="estadoPago")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LiquidacionCreate(LiquidacionBase):
    pass


class GenerarLiquidacionRequest(BaseModel):
    periodo: str
    id_agencia: int | None = Field(default=None, alias="idAgencia")

    model_config = ConfigDict(populate_by_name=True)


class LiquidacionUpdate(BaseModel):
    monto_ventas: Optional[Decimal] = Field(default=None, alias="montoVentas")
    comision_plataforma: Optional[Decimal] = Field(default=None, alias="comisionPlataforma")
    monto_a_transferir: Optional[Decimal] = Field(default=None, alias="montoATransferir")
    estado_pago: Optional[str] = Field(default=None, alias="estadoPago")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LiquidacionOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_liquidacion_agencia")
    id_agencia: int = Field(alias="idAgencia")
    periodo: str
    monto_ventas: Decimal = Field(alias="montoVentas")
    comision_plataforma: Decimal = Field(alias="comisionPlataforma")
    monto_a_transferir: Decimal = Field(alias="montoATransferir")
    estado_pago: str = Field(alias="estadoPago")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── ApiKey ────────────────────────────────────────────────────────────────────

class ApiKeyBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    token: str
    fecha_expiracion: datetime = Field(alias="fechaExpiracion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyUpdate(BaseModel):
    estado: Optional[bool] = None
    fecha_expiracion: Optional[datetime] = Field(default=None, alias="fechaExpiracion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApiKeyOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_api_key")
    id_agencia: int = Field(alias="idAgencia")
    token: str
    fecha_creacion: datetime = Field(alias="fechaCreacion")
    fecha_expiracion: datetime = Field(alias="fechaExpiracion")
    ultimo_uso: Optional[datetime] = Field(default=None, alias="ultimoUso")
    activo: bool = Field(validation_alias="estado")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
