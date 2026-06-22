from fastapi import APIRouter

from app.dependencies import ApiKeyAuth, DbDep
from app.modules.public import service
from app.modules.public.schemas import BoletoExternoCreate, BoletoExternoOut

router = APIRouter(prefix="/api/v1", tags=["API Publica"])


@router.get("/viajes/{id_viaje}/asientos")
async def list_asientos_disponibles(id_viaje: int, db: DbDep, _: ApiKeyAuth):
    return await service.get_asientos_disponibles(db, id_viaje)


@router.post("/boletos", response_model=BoletoExternoOut, status_code=201)
async def crear_boleto_externo(body: BoletoExternoCreate, db: DbDep, api_key: ApiKeyAuth):
    return await service.create_boleto_externo(db, body, api_key["id_agencia"])
