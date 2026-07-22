from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.suscripciones.models import Plan, Suscripcion
from app.modules.suscripciones.schemas import (
    PlanCreate,
    PlanUpdate,
    SuscripcionCreate,
    SuscripcionUpdate,
)


# ── Planes ────────────────────────────────────────────────────────────────────

async def get_all_planes(db: AsyncSession) -> list[Plan]:
    result = await db.execute(select(Plan).order_by(Plan.precio))
    return list(result.scalars().all())


async def get_plan_by_id(db: AsyncSession, id_plan: int) -> Plan:
    result = await db.execute(select(Plan).where(Plan.id_plan == id_plan))
    p = result.scalar_one_or_none()
    if not p:
        raise NotFoundException(f"Plan {id_plan} no encontrado")
    return p


async def create_plan(db: AsyncSession, data: PlanCreate) -> Plan:
    p = Plan(nombre=data.nombre, precio=data.precio, limite_buses=data.limite_buses)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


async def update_plan(db: AsyncSession, id_plan: int, data: PlanUpdate) -> Plan:
    p = await get_plan_by_id(db, id_plan)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(p, key, value)
    await db.commit()
    await db.refresh(p)
    return p


async def delete_plan(db: AsyncSession, id_plan: int) -> dict:
    p = await get_plan_by_id(db, id_plan)
    tiene_suscripciones = await db.execute(
        select(func.count()).select_from(Suscripcion).where(Suscripcion.id_plan == id_plan)
    )
    if tiene_suscripciones.scalar() > 0:
        raise ConflictException(
            f"No se puede eliminar el plan {id_plan}: tiene suscripciones asociadas"
        )
    await db.delete(p)
    await db.commit()
    return {"message": f"Plan {id_plan} eliminado"}


# ── Suscripciones ─────────────────────────────────────────────────────────────

async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Suscripcion]:
    result = await db.execute(select(Suscripcion).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_agencia(db: AsyncSession, id_agencia: int) -> list[Suscripcion]:
    result = await db.execute(
        select(Suscripcion).where(Suscripcion.id_agencia == id_agencia)
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_suscripcion: int) -> Suscripcion:
    result = await db.execute(
        select(Suscripcion).where(Suscripcion.id_suscripcion == id_suscripcion)
    )
    s = result.scalar_one_or_none()
    if not s:
        raise NotFoundException(f"Suscripcion {id_suscripcion} no encontrada")
    return s


async def create(db: AsyncSession, data: SuscripcionCreate) -> Suscripcion:
    s = Suscripcion(
        id_agencia=data.id_agencia,
        id_plan=data.id_plan,
        monto_mensual=data.monto_mensual,
        fecha_facturacion=data.fecha_facturacion,
        estado_cobro=data.estado_cobro,
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


async def update_suscripcion(
    db: AsyncSession, id_suscripcion: int, data: SuscripcionUpdate
) -> Suscripcion:
    s = await get_by_id(db, id_suscripcion)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(s, key, value)
    await db.commit()
    await db.refresh(s)
    return s


async def delete_suscripcion(db: AsyncSession, id_suscripcion: int) -> dict:
    s = await get_by_id(db, id_suscripcion)
    await db.delete(s)
    await db.commit()
    return {"message": f"Suscripcion {id_suscripcion} eliminada"}
