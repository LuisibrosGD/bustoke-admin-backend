from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Chofer(Base):
    __tablename__ = "choferes"

    id_chofer: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    id_tipo_documento: Mapped[int] = mapped_column(
        Integer, ForeignKey("tipos_documento.id_tipo_documento"), nullable=False
    )
    numero_documento: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[str] = mapped_column(String(100), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
