from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.manifiestos.models import ManifiestoSutran
from app.modules.manifiestos.schemas import ManifiestoDetalleOut


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 200) -> list[ManifiestoSutran]:
    result = await db.execute(select(ManifiestoSutran).offset(skip).limit(limit).order_by(ManifiestoSutran.fecha_generacion.desc()))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id_manifiesto: int) -> ManifiestoDetalleOut | None:
    sql = text("""
        SELECT
            m.id_manifiesto,
            m.id_viaje,
            m.fecha_generacion,
            m.estado_envio,
            m.respuesta_api,
            v.fecha_hora_salida,
            v.fecha_hora_llegada,
            v.estado         AS viaje_estado,
            v.rampa_embarque,
            b.placa          AS placa_bus,
            tor.nombre       AS ruta_origen,
            tdes.nombre      AS ruta_destino
        FROM manifiestos_sutran m
        JOIN viajes     v    ON m.id_viaje = v.id_viaje
        JOIN buses      b    ON v.id_bus   = b.id_bus
        JOIN rutas      r    ON v.id_ruta  = r.id_ruta
        JOIN terminales tor  ON r.id_terminal_origen  = tor.id_terminal
        JOIN terminales tdes ON r.id_terminal_destino = tdes.id_terminal
        WHERE m.id_manifiesto = :id
    """)
    result = await db.execute(sql, {"id": id_manifiesto})
    row = result.mappings().one_or_none()
    if not row:
        return None
    return ManifiestoDetalleOut(
        id=row["id_manifiesto"],
        idViaje=row["id_viaje"],
        fechaGeneracion=row["fecha_generacion"],
        estadoEnvio=row["estado_envio"],
        respuestaApi=row["respuesta_api"],
        fechaHoraSalida=row["fecha_hora_salida"],
        fechaHoraLlegada=row["fecha_hora_llegada"],
        viajeEstado=row["viaje_estado"],
        rampaEmbarque=row["rampa_embarque"],
        placaBus=row["placa_bus"],
        rutaOrigen=row["ruta_origen"],
        rutaDestino=row["ruta_destino"],
    )
