from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.modules.viajes.models import EstadoPago


class LiquidacionAgencia(Base):
    __tablename__ = "liquidaciones_agencia"

    id_liquidacion_agencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    periodo: Mapped[str] = mapped_column(String(7), nullable=False)
    monto_ventas: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    comision_plataforma: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monto_a_transferir: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado_pago: Mapped[EstadoPago] = mapped_column(
        SAEnum(EstadoPago, name="estado_pago", create_type=False),
        nullable=False,
        default=EstadoPago.pendiente,
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id_api_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    fecha_expiracion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ultimo_uso: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
