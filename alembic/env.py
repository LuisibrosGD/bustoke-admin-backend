import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Importar modelos para que Alembic los detecte ────────────────────────────
from app.database import Base  # noqa: F401 — activa el metadata

# Módulos — importar todos los modelos
from app.modules.auth.models import Usuario  # noqa: F401
from app.modules.agencias.models import Agencia  # noqa: F401
from app.modules.flota.models import Bus, Asiento  # noqa: F401
from app.modules.rutas.models import Ruta, TarifaRuta  # noqa: F401
from app.modules.viajes.models import Viaje, Pasajero, Boleto  # noqa: F401
from app.modules.terminales.models import Terminal  # noqa: F401
from app.modules.suscripciones.models import Plan, Suscripcion  # noqa: F401
from app.modules.soporte.models import HistorialCambioSoporte, TicketSoporte  # noqa: F401
from app.modules.notificaciones.models import Notificacion  # noqa: F401
from app.modules.reclamos.models import MensajeReclamo, Reclamo  # noqa: F401
from app.modules.finanzas.models import LiquidacionAgencia, ApiKey  # noqa: F401
from app.modules.ubigeo.models import Departamento, Provincia, Distrito  # noqa: F401
from app.modules.agencias_terminales.models import AgenciaTerminal  # noqa: F401
from app.modules.choferes.models import Chofer  # noqa: F401

# ─────────────────────────────────────────────────────────────────────────────

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
