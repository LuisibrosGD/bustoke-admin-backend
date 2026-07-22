from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.manifiestos.models import ManifiestoSutran
from app.modules.manifiestos.schemas import ManifiestoDetalleOut
from app.modules.rutas.models import Ruta
from app.modules.viajes.models import Viaje


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 200,
    id_agencia: int | None = None,
    id_terminal: int | None = None,
) -> list[ManifiestoSutran]:
    query = select(ManifiestoSutran)
    if id_agencia or id_terminal:
        query = query.join(Viaje, Viaje.id_viaje == ManifiestoSutran.id_viaje).join(
            Ruta, Ruta.id_ruta == Viaje.id_ruta
        )
        if id_agencia:
            query = query.where(Ruta.id_agencia == id_agencia)
        if id_terminal:
            query = query.where(
                or_(Ruta.id_terminal_origen == id_terminal, Ruta.id_terminal_destino == id_terminal)
            )
    query = query.offset(skip).limit(limit).order_by(ManifiestoSutran.fecha_generacion.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, id_manifiesto: int, id_agencia: int | None = None, id_terminal: int | None = None
) -> ManifiestoDetalleOut | None:
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
          AND (CAST(:id_agencia AS INTEGER) IS NULL OR b.id_agencia = CAST(:id_agencia AS INTEGER))
          AND (
            CAST(:id_terminal AS INTEGER) IS NULL
            OR r.id_terminal_origen = CAST(:id_terminal AS INTEGER)
            OR r.id_terminal_destino = CAST(:id_terminal AS INTEGER)
          )
    """)
    result = await db.execute(
        sql, {"id": id_manifiesto, "id_agencia": id_agencia, "id_terminal": id_terminal}
    )
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
