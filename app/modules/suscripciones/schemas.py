from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Planes ────────────────────────────────────────────────────────────────────

class PlanBase(BaseModel):
    nombre: str
    precio: Decimal
    limite_buses: int = Field(alias="limiteBuses")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[Decimal] = None
    limite_buses: Optional[int] = Field(default=None, alias="limiteBuses")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PlanOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_plan")
    nombre: str
    precio: Decimal
    limite_buses: int = Field(alias="limiteBuses")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Suscripciones ─────────────────────────────────────────────────────────────

class SuscripcionBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    id_plan: int = Field(alias="idPlan")
    monto_mensual: Decimal = Field(alias="montoMensual")
    fecha_facturacion: date = Field(alias="fechaFacturacion")
    estado_cobro: str = Field(default="pendiente", alias="estadoCobro")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SuscripcionCreate(SuscripcionBase):
    pass


class SuscripcionUpdate(BaseModel):
    monto_mensual: Optional[Decimal] = Field(default=None, alias="montoMensual")
    fecha_facturacion: Optional[date] = Field(default=None, alias="fechaFacturacion")
    estado_cobro: Optional[str] = Field(default=None, alias="estadoCobro")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SuscripcionOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_suscripcion")
    id_agencia: int = Field(alias="idAgencia")
    id_plan: int = Field(alias="idPlan")
    monto_mensual: Decimal = Field(alias="montoMensual")
    fecha_facturacion: date = Field(alias="fechaFacturacion")
    estado_cobro: str = Field(alias="estadoCobro")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
