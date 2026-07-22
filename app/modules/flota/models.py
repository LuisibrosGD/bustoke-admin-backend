import enum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoServicio(str, enum.Enum):
    vip = "vip"
    normal = "normal"


class TipoAmenidad(str, enum.Enum):
    tv = "tv"
    bano = "bano"
    escaleras = "escaleras"
    cafetera = "cafetera"


class Bus(Base):
    __tablename__ = "buses"

    id_bus: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    cantidad_pisos: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    asientos: Mapped[list["Asiento"]] = relationship("Asiento", back_populates="bus", lazy="select")


class Asiento(Base):
    __tablename__ = "asientos"

    id_asiento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_bus: Mapped[int] = mapped_column(Integer, ForeignKey("buses.id_bus"), nullable=False)
    numero_asiento: Mapped[str] = mapped_column(String(10), nullable=False)
    fila: Mapped[str] = mapped_column(String(5), nullable=False)
    piso: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tipo_servicio: Mapped[TipoServicio] = mapped_column(
        SAEnum(TipoServicio, name="tipo_servicio", create_type=False),
        nullable=False,
        default=TipoServicio.normal,
    )
    coord_x: Mapped[int] = mapped_column(Integer, nullable=False)
    coord_y: Mapped[int] = mapped_column(Integer, nullable=False)
    bloqueado_manual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    bus: Mapped["Bus"] = relationship("Bus", back_populates="asientos")


class AmenidadBus(Base):
    """Elemento no-asiento del plano del bus (TV, baño, escaleras, cafetera).
    Puramente informativo/visual: a diferencia de Asiento, nada más hace
    referencia a esta tabla, así que se reemplaza completa en cada guardado
    de plantilla (sin el problema de FKs que sí tiene Asiento con Boleto)."""

    __tablename__ = "amenidades_bus"

    id_amenidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_bus: Mapped[int] = mapped_column(Integer, ForeignKey("buses.id_bus"), nullable=False)
    tipo: Mapped[TipoAmenidad] = mapped_column(
        SAEnum(TipoAmenidad, name="tipo_amenidad", create_type=False),
        nullable=False,
    )
    piso: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    coord_x: Mapped[int] = mapped_column(Integer, nullable=False)
    coord_y: Mapped[int] = mapped_column(Integer, nullable=False)
