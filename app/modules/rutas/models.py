from decimal import Decimal

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.flota.models import TipoServicio


class Ruta(Base):
    __tablename__ = "rutas"

    id_ruta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    id_terminal_origen: Mapped[int] = mapped_column(
        Integer, ForeignKey("terminales.id_terminal"), nullable=False
    )
    id_terminal_destino: Mapped[int] = mapped_column(
        Integer, ForeignKey("terminales.id_terminal"), nullable=False
    )
    tarifa_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    tarifas: Mapped[list["TarifaRuta"]] = relationship(
        "TarifaRuta", back_populates="ruta", lazy="select"
    )


class TarifaRuta(Base):
    __tablename__ = "tarifas_ruta"

    id_tarifa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_ruta: Mapped[int] = mapped_column(Integer, ForeignKey("rutas.id_ruta"), nullable=False)
    tipo_servicio: Mapped[TipoServicio] = mapped_column(
        SAEnum(TipoServicio, name="tipo_servicio", create_type=False), nullable=False
    )
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    ruta: Mapped["Ruta"] = relationship("Ruta", back_populates="tarifas")
