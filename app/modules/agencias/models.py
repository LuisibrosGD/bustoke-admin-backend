import enum
from typing import Optional

from sqlalchemy import Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EstadoAgencia(str, enum.Enum):
    activa = "activa"
    suspendida = "suspendida"


class Agencia(Base):
    __tablename__ = "agencias"

    id_agencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ruc: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    razon_social: Mapped[str] = mapped_column(String(205), nullable=False)
    estado: Mapped[EstadoAgencia] = mapped_column(
        SAEnum(EstadoAgencia, name="estado_agencia", create_type=False),
        nullable=False,
        default=EstadoAgencia.activa,
    )
    banco_nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    numero_cuenta: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cuenta_cci: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
