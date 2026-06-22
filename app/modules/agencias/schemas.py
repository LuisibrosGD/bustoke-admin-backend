from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AgenciaBase(BaseModel):
    ruc: str
    razon_social: str = Field(alias="razonSocial")
    estado: str = "activa"
    banco_nombre: Optional[str] = Field(default=None, alias="bancoNombre")
    numero_cuenta: Optional[str] = Field(default=None, alias="numeroCuenta")
    cuenta_cci: Optional[str] = Field(default=None, alias="cuentaCci")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AgenciaCreate(AgenciaBase):
    pass


class AgenciaUpdate(BaseModel):
    ruc: Optional[str] = None
    razon_social: Optional[str] = Field(default=None, alias="razonSocial")
    estado: Optional[str] = None
    banco_nombre: Optional[str] = Field(default=None, alias="bancoNombre")
    numero_cuenta: Optional[str] = Field(default=None, alias="numeroCuenta")
    cuenta_cci: Optional[str] = Field(default=None, alias="cuentaCci")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AgenciaOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_agencia")
    ruc: str
    razon_social: str = Field(alias="razonSocial")
    estado: str
    banco_nombre: Optional[str] = Field(default=None, alias="bancoNombre")
    numero_cuenta: Optional[str] = Field(default=None, alias="numeroCuenta")
    cuenta_cci: Optional[str] = Field(default=None, alias="cuentaCci")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
