import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EstadoReclamo(str, enum.Enum):
    abierto = "abierto"
    en_proceso = "en_proceso"
    resuelto = "resuelto"


class Reclamo(Base):
    __tablename__ = "reclamos"

    id_reclamo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    motivo: Mapped[str] = mapped_column(String(150), nullable=False)
    detalle: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoReclamo] = mapped_column(
        SAEnum(EstadoReclamo, name="estado_reclamo", create_type=False),
        nullable=False,
        default=EstadoReclamo.abierto,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    mensajes: Mapped[list["MensajeReclamo"]] = relationship(
        "MensajeReclamo", back_populates="reclamo", cascade="all, delete-orphan"
    )


class MensajeReclamo(Base):
    __tablename__ = "mensajes_reclamo"

    id_mensaje: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_reclamo: Mapped[int] = mapped_column(
        Integer, ForeignKey("reclamos.id_reclamo"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=False
    )
    text_mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    reclamo: Mapped["Reclamo"] = relationship("Reclamo", back_populates="mensajes")
