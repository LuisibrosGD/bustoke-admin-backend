from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AgenciaTerminalBase(BaseModel):
    id_agencia: int = Field(alias="idAgencia")
    id_terminal: int = Field(alias="idTerminal")
    nro_counter_oficina: str = Field(alias="nroCounterOficina")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AgenciaTerminalCreate(AgenciaTerminalBase):
    pass


class AgenciaTerminalOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_agencia_terminal")
    id_agencia: int = Field(alias="idAgencia")
    id_terminal: int = Field(alias="idTerminal")
    nro_counter_oficina: str = Field(alias="nroCounterOficina")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
