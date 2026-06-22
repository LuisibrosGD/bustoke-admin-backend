from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.manifiestos.models import ManifiestoSutran


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 200) -> list[ManifiestoSutran]:
    result = await db.execute(select(ManifiestoSutran).offset(skip).limit(limit).order_by(ManifiestoSutran.fecha_generacion.desc()))
    return list(result.scalars().all())
