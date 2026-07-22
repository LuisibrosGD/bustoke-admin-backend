from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.choferes.models import Chofer
from app.modules.choferes.schemas import ChoferCreate, ChoferUpdate
from app.modules.ubigeo.models import TipoDocumento
from app.modules.viajes.models import Viaje


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Chofer]:
    result = await db.execute(select(Chofer).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_chofer: int) -> Chofer:
    result = await db.execute(select(Chofer).where(Chofer.id_chofer == id_chofer))
    chofer = result.scalar_one_or_none()
    if not chofer:
        raise NotFoundException(f"Chofer {id_chofer} no encontrado")
    return chofer


async def get_by_agencia(db: AsyncSession, id_agencia: int) -> list[Chofer]:
    result = await db.execute(select(Chofer).where(Chofer.id_agencia == id_agencia))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: ChoferCreate) -> Chofer:
    existing = await db.execute(
        select(Chofer).where(Chofer.numero_documento == data.numero_documento)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(
            f"Ya existe un chofer con documento {data.numero_documento}"
        )
    chofer = Chofer(
        id_agencia=data.id_agencia,
        id_tipo_documento=data.id_tipo_documento,
        numero_documento=data.numero_documento,
        nombres=data.nombres,
        apellido_paterno=data.apellido_paterno,
        apellido_materno=data.apellido_materno,
        activo=data.activo,
    )
    db.add(chofer)
    await db.commit()
    await db.refresh(chofer)
    return chofer


async def bulk_create(db: AsyncSession, id_agencia: int, rows: list[dict]) -> dict:
    """Carga masiva de choferes desde un Excel ya parseado (ver app/core/excel.py).
    Reutiliza create() fila por fila, así que hereda su validación de
    documento duplicado (ConflictException -> se cuenta como omitido)."""
    tipos_result = await db.execute(select(TipoDocumento.id_tipo_documento, TipoDocumento.nombre))
    tipos_by_nombre = {nombre.strip().lower(): tid for tid, nombre in tipos_result.all()}

    success = 0
    skipped = 0
    errors: list[dict] = []
    for i, row in enumerate(rows, start=2):  # fila 1 = encabezados
        try:
            tipo_doc = str(row.get("Tipo Documento") or "").strip()
            numero_doc = str(row.get("Número Documento") or "").strip()
            nombres = str(row.get("Nombres") or "").strip()
            ap_paterno = str(row.get("Apellido Paterno") or "").strip()
            ap_materno = str(row.get("Apellido Materno") or "").strip()

            id_tipo_documento = tipos_by_nombre.get(tipo_doc.lower())
            if not id_tipo_documento:
                raise ValueError(f"Tipo Documento '{tipo_doc}' no existe")
            if not numero_doc:
                raise ValueError("Número Documento es requerido")
            if not nombres or not ap_paterno or not ap_materno:
                raise ValueError("Nombres, Apellido Paterno y Apellido Materno son requeridos")

            data = ChoferCreate(
                id_agencia=id_agencia,
                id_tipo_documento=id_tipo_documento,
                numero_documento=numero_doc,
                nombres=nombres,
                apellido_paterno=ap_paterno,
                apellido_materno=ap_materno,
            )
            await create(db, data)
            success += 1
        except ConflictException:
            skipped += 1
        except Exception as e:
            await db.rollback()
            errors.append({"row": i, "message": str(e)})

    return {
        "totalProcessed": len(rows),
        "successCount": success,
        "skippedCount": skipped,
        "errorCount": len(errors),
        "errors": errors,
    }


async def update(db: AsyncSession, id_chofer: int, data: ChoferUpdate) -> Chofer:
    chofer = await get_by_id(db, id_chofer)
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(chofer, key, value)
    await db.commit()
    await db.refresh(chofer)
    return chofer


async def delete(db: AsyncSession, id_chofer: int) -> dict:
    chofer = await get_by_id(db, id_chofer)
    tiene_viajes = await db.execute(
        select(func.count()).select_from(Viaje).where(Viaje.id_chofer == id_chofer)
    )
    if tiene_viajes.scalar() > 0:
        raise ConflictException(
            f"No se puede eliminar el chofer {id_chofer}: tiene viajes asignados"
        )
    await db.delete(chofer)
    await db.commit()
    return {"message": f"Chofer {id_chofer} eliminado"}
