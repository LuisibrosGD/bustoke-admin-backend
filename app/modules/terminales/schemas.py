from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TerminalBase(BaseModel):
    id_distrito: int = Field(alias="idDistrito")
    nombre: str
    direccion: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TerminalCreate(TerminalBase):
    pass


class TerminalUpdate(BaseModel):
    id_distrito: Optional[int] = Field(default=None, alias="idDistrito")
    nombre: Optional[str] = None
    direccion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TerminalOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_terminal")
    id_distrito: int = Field(alias="idDistrito")
    nombre: str
    direccion: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
