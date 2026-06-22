from pydantic import BaseModel, ConfigDict, Field


class DepartamentoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_departamento")
    nombre: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProvinciaOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_provincia")
    id_departamento: int = Field(alias="idDepartamento")
    nombre: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DistritoOut(BaseModel):
    id: int = Field(alias="id", validation_alias="id_distrito")
    id_provincia: int = Field(alias="idProvincia")
    nombre: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
