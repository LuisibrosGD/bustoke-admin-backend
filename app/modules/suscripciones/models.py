from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.viajes.models import EstadoPago


class Plan(Base):
    __tablename__ = "planes"

    id_plan: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    limite_buses: Mapped[int] = mapped_column(Integer, nullable=False)


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id_suscripcion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    id_plan: Mapped[int] = mapped_column(Integer, ForeignKey("planes.id_plan"), nullable=False)
    monto_mensual: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_facturacion: Mapped[date] = mapped_column(Date, nullable=False)
    estado_cobro: Mapped[EstadoPago] = mapped_column(
        SAEnum(EstadoPago, name="estado_pago", create_type=False),
        nullable=False,
        default=EstadoPago.pendiente,
    )
