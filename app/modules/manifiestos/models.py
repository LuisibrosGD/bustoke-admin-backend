from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ManifiestoSutran(Base):
    __tablename__ = "manifiestos_sutran"

    id_manifiesto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_viaje: Mapped[int] = mapped_column(Integer, ForeignKey("viajes.id_viaje"), nullable=False)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    estado_envio: Mapped[str] = mapped_column(String(30), nullable=False)
    respuesta_api: Mapped[str] = mapped_column(Text, nullable=False)
