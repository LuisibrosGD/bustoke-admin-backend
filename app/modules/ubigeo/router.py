from fastapi import APIRouter

from app.dependencies import DbDep
from app.modules.ubigeo import service
from app.modules.ubigeo.schemas import DepartamentoOut, DistritoOut, ProvinciaOut

router = APIRouter(prefix="/admin/ubigeo", tags=["Ubigeo"])


@router.get("/departamentos", response_model=list[DepartamentoOut])
async def list_departamentos(db: DbDep):
    return await service.get_departamentos(db)


@router.get("/provincias", response_model=list[ProvinciaOut])
async def list_provincias(db: DbDep, id_departamento: int | None = None):
    return await service.get_provincias(db, id_departamento)


@router.get("/distritos", response_model=list[DistritoOut])
async def list_distritos(db: DbDep, id_provincia: int | None = None):
    return await service.get_distritos(db, id_provincia)
