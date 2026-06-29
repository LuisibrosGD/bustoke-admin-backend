import enum
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.flota.models import TipoServicio


class EstadoViaje(str, enum.Enum):
    programado = "programado"
    en_curso = "en_curso"
    finalizado = "finalizado"
    cancelado = "cancelado"


class EstadoBoleto(str, enum.Enum):
    activo = "activo"
    cancelado = "cancelado"


class MetodoPago(str, enum.Enum):
    yape = "yape"
    plin = "plin"
    tarjeta = "tarjeta"


class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    completado = "completado"
    fallido = "fallido"
    reembolsado = "reembolsado"


class CanalVenta(str, enum.Enum):
    app_bustoke = "app_bustoke"
    ventanilla_fisica = "ventanilla_fisica"
    api_externa = "api_externa"


class Viaje(Base):
    __tablename__ = "viajes"

    id_viaje: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_ruta: Mapped[int] = mapped_column(Integer, ForeignKey("rutas.id_ruta"), nullable=False)
    id_bus: Mapped[int] = mapped_column(Integer, ForeignKey("buses.id_bus"), nullable=False)
    id_chofer: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("choferes.id_chofer"), nullable=True
    )
    fecha_hora_salida: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_hora_llegada: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estado: Mapped[EstadoViaje] = mapped_column(
        SAEnum(EstadoViaje, name="estado_viaje", create_type=False),
        nullable=False,
        default=EstadoViaje.programado,
    )
    rampa_embarque: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Por asignar"
    )


class Pasajero(Base):
    __tablename__ = "pasajeros"

    id_pasajero: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=True
    )
    id_tipo_documento: Mapped[int] = mapped_column(
        Integer, ForeignKey("tipos_documento.id_tipo_documento"), nullable=False
    )
    numero_documento: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class Boleto(Base):
    __tablename__ = "boletos"

    id_boleto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_viaje: Mapped[int] = mapped_column(Integer, ForeignKey("viajes.id_viaje"), nullable=False)
    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=True
    )
    id_pasajero: Mapped[int] = mapped_column(
        Integer, ForeignKey("pasajeros.id_pasajero"), nullable=False
    )
    id_asiento: Mapped[int] = mapped_column(
        Integer, ForeignKey("asientos.id_asiento"), nullable=False
    )
    email_contacto: Mapped[str] = mapped_column(String(150), nullable=False)
    canal: Mapped[CanalVenta] = mapped_column(
        SAEnum(CanalVenta, name="canal_venta", create_type=False), nullable=False
    )
    codigo_qr: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fecha_validacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    precio_final: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    estado: Mapped[EstadoBoleto] = mapped_column(
        SAEnum(EstadoBoleto, name="estado_boleto", create_type=False),
        nullable=False,
        default=EstadoBoleto.activo,
    )
    estado_checkin: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pendiente"
    )
    acepto_terminos_politicas: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ip_registro: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
