import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.flota.models import Asiento
from app.modules.flota.service import get_asientos_by_bus
from app.modules.viajes.models import Boleto, CanalVenta, Pasajero
from app.modules.viajes.service import get_viaje_by_id
from app.modules.public.schemas import BoletoExternoCreate


async def get_asientos_disponibles(
    db: AsyncSession, id_viaje: int
) -> list[dict]:
    viaje = await get_viaje_by_id(db, id_viaje)
    asientos = await get_asientos_by_bus(db, viaje.id_bus)

    boletos_result = await db.execute(
        select(Boleto.id_asiento).where(Boleto.id_viaje == id_viaje)
    )
    ids_ocupados = {row[0] for row in boletos_result.all()}

    result = []
    for a in asientos:
        result.append({
            "id_asiento": a.id_asiento,
            "numero_asiento": a.numero_asiento,
            "fila": a.fila,
            "piso": a.piso,
            "tipo_servicio": a.tipo_servicio,
            "ocupado": a.id_asiento in ids_ocupados,
            "bloqueado": a.bloqueado_manual,
        })
    return result


async def create_boleto_externo(
    db: AsyncSession, data: BoletoExternoCreate, id_agencia: int
) -> Boleto:
    viaje = await get_viaje_by_id(db, data.id_viaje)

    asiento_result = await db.execute(
        select(Asiento).where(Asiento.id_asiento == data.id_asiento)
    )
    asiento = asiento_result.scalar_one_or_none()
    if not asiento:
        raise NotFoundException(f"Asiento {data.id_asiento} no encontrado")

    boleto_existente = await db.execute(
        select(Boleto).where(
            Boleto.id_viaje == data.id_viaje,
            Boleto.id_asiento == data.id_asiento,
            Boleto.estado == "activo",
        )
    )
    if boleto_existente.scalar_one_or_none():
        raise BadRequestException("El asiento ya se encuentra ocupado")

    pasajero = Pasajero(
        id_tipo_documento=data.pasajero.id_tipo_documento,
        numero_documento=data.pasajero.numero_documento,
        nombres=data.pasajero.nombres,
        apellido_paterno=data.pasajero.apellido_paterno,
        apellido_materno=data.pasajero.apellido_materno,
        fecha_nacimiento=data.pasajero.fecha_nacimiento,
    )
    db.add(pasajero)
    await db.flush()

    codigo_qr = f"BKT-EXT-{data.id_viaje}-{data.id_asiento}-{secrets.token_hex(4).upper()}"

    boleto = Boleto(
        id_viaje=data.id_viaje,
        id_pasajero=pasajero.id_pasajero,
        id_asiento=data.id_asiento,
        email_contacto=data.email_contacto,
        canal=CanalVenta.api_externa,
        codigo_qr=codigo_qr,
        precio_final=data.precio_final,
    )
    db.add(boleto)
    await db.commit()
    await db.refresh(boleto)
    return boleto
