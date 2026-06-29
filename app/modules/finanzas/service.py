import secrets

from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.modules.finanzas.models import ApiKey, LiquidacionAgencia
from app.modules.finanzas.schemas import (
    ApiKeyCreate,
    ApiKeyUpdate,
    LiquidacionCreate,
    LiquidacionUpdate,
)
from app.modules.viajes.models import Boleto, Viaje
from app.modules.rutas.models import Ruta


# ── Liquidaciones ─────────────────────────────────────────────────────────────

async def get_all_liquidaciones(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[LiquidacionAgencia]:
    result = await db.execute(select(LiquidacionAgencia).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_liquidaciones_by_agencia(
    db: AsyncSession, id_agencia: int
) -> list[LiquidacionAgencia]:
    result = await db.execute(
        select(LiquidacionAgencia).where(LiquidacionAgencia.id_agencia == id_agencia)
    )
    return list(result.scalars().all())


async def get_liquidacion_by_id(db: AsyncSession, id_liquidacion: int) -> LiquidacionAgencia:
    result = await db.execute(
        select(LiquidacionAgencia).where(
            LiquidacionAgencia.id_liquidacion_agencia == id_liquidacion
        )
    )
    liq = result.scalar_one_or_none()
    if not liq:
        raise NotFoundException(f"Liquidacion {id_liquidacion} no encontrada")
    return liq


async def create_liquidacion(db: AsyncSession, data: LiquidacionCreate) -> LiquidacionAgencia:
    liq = LiquidacionAgencia(
        id_agencia=data.id_agencia,
        periodo=data.periodo,
        monto_ventas=data.monto_ventas,
        comision_plataforma=data.comision_plataforma,
        monto_a_transferir=data.monto_a_transferir,
        estado_pago=data.estado_pago,
    )
    db.add(liq)
    await db.commit()
    await db.refresh(liq)
    return liq


async def update_liquidacion(
    db: AsyncSession, id_liquidacion: int, data: LiquidacionUpdate
) -> LiquidacionAgencia:
    liq = await get_liquidacion_by_id(db, id_liquidacion)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(liq, key, value)
    await db.commit()
    await db.refresh(liq)
    return liq


async def delete_liquidacion(db: AsyncSession, id_liquidacion: int) -> dict:
    liq = await get_liquidacion_by_id(db, id_liquidacion)
    await db.delete(liq)
    await db.commit()
    return {"message": f"Liquidacion {id_liquidacion} eliminada"}


async def generar_liquidaciones(
    db: AsyncSession, periodo: str, id_agencia: int | None = None
) -> list[LiquidacionAgencia]:
    if not (len(periodo) == 7 and periodo[4] == "-"):
        raise BadRequestException("periodo debe tener formato YYYY-MM")

    result = await db.execute(
        select(
            Ruta.id_agencia,
            func.coalesce(func.sum(Boleto.precio_final), 0).label("total_ventas"),
        )
        .select_from(Boleto)
        .join(Viaje, Boleto.id_viaje == Viaje.id_viaje)
        .join(Ruta, Viaje.id_ruta == Ruta.id_ruta)
        .where(
            func.to_char(Boleto.fecha_emision, literal_column("'YYYY-MM'")) == periodo,
            Boleto.estado != "cancelado",
        )
        .group_by(Ruta.id_agencia)
    )
    rows = result.all()

    created: list[LiquidacionAgencia] = []
    for row in rows:
        agencia_id = row[0]
        total_ventas = row[1]

        if id_agencia is not None and agencia_id != id_agencia:
            continue

        existing = await db.execute(
            select(LiquidacionAgencia).where(
                LiquidacionAgencia.id_agencia == agencia_id,
                LiquidacionAgencia.periodo == periodo,
            )
        )
        if existing.scalar_one_or_none():
            continue

        liq = LiquidacionAgencia(
            id_agencia=agencia_id,
            periodo=periodo,
            monto_ventas=total_ventas,
            comision_plataforma=0,
            monto_a_transferir=0,
            estado_pago="pendiente",
        )
        db.add(liq)
        await db.flush()
        await db.refresh(liq)
        created.append(liq)

    if not created:
        raise BadRequestException(
            "No se generaron liquidaciones. "
            "Puede que ya existan o no haya boletos en ese periodo."
        )

    await db.commit()
    return created


# ── ApiKeys ───────────────────────────────────────────────────────────────────

async def get_all_api_keys(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ApiKey]:
    result = await db.execute(select(ApiKey).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_api_keys_by_agencia(db: AsyncSession, id_agencia: int) -> list[ApiKey]:
    result = await db.execute(select(ApiKey).where(ApiKey.id_agencia == id_agencia))
    return list(result.scalars().all())


async def get_api_key_by_id(db: AsyncSession, id_api_key: int) -> ApiKey:
    result = await db.execute(select(ApiKey).where(ApiKey.id_api_key == id_api_key))
    key = result.scalar_one_or_none()
    if not key:
        raise NotFoundException(f"ApiKey {id_api_key} no encontrada")
    return key


async def create_api_key(db: AsyncSession, data: ApiKeyCreate) -> ApiKey:
    existing = await db.execute(
        select(func.count()).select_from(ApiKey).where(ApiKey.id_agencia == data.id_agencia)
    )
    if existing.scalar() > 0:
        raise BadRequestException("La agencia ya tiene una API Key registrada")
    token = data.token if data.token else secrets.token_urlsafe(32)
    fecha_expiracion = data.fecha_expiracion.replace(tzinfo=None) if data.fecha_expiracion.tzinfo else data.fecha_expiracion
    key = ApiKey(
        id_agencia=data.id_agencia,
        token=token,
        fecha_expiracion=fecha_expiracion,
    )
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return key


async def update_api_key(db: AsyncSession, id_api_key: int, data: ApiKeyUpdate) -> ApiKey:
    key = await get_api_key_by_id(db, id_api_key)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for k, v in update_data.items():
        setattr(key, k, v)
    await db.commit()
    await db.refresh(key)
    return key


async def get_api_key_by_token(db: AsyncSession, token: str) -> ApiKey | None:
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.token == token,
            ApiKey.estado == True,
            ApiKey.fecha_expiracion > func.now(),
        )
    )
    return result.scalar_one_or_none()


async def delete_api_key(db: AsyncSession, id_api_key: int) -> dict:
    key = await get_api_key_by_id(db, id_api_key)
    await db.delete(key)
    await db.commit()
    return {"message": f"ApiKey {id_api_key} eliminada"}
