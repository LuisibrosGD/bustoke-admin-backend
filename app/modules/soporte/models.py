import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EstadoTicket(str, enum.Enum):
    abierto = "abierto"
    en_revision = "en_revision"
    resuelto = "resuelto"


class TicketSoporte(Base):
    __tablename__ = "tickets_soporte"

    id_ticket_soporte: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    asunto: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoTicket] = mapped_column(
        SAEnum(EstadoTicket, name="estado_ticket", create_type=False),
        nullable=False,
        default=EstadoTicket.abierto,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


class HistorialCambioSoporte(Base):
    __tablename__ = "historial_cambios_soporte"

    id_historial: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_ticket: Mapped[int] = mapped_column(
        Integer, ForeignKey("tickets_soporte.id_ticket_soporte"), nullable=False
    )
    campo: Mapped[str] = mapped_column(String(30), nullable=False)
    valor_anterior: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    valor_nuevo: Mapped[str] = mapped_column(String(50), nullable=False)
    id_usuario_modifica: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=True
    )
    fecha_cambio: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
