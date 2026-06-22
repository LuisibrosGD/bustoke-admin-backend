from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Terminal(Base):
    __tablename__ = "terminales"

    id_terminal: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_distrito: Mapped[int] = mapped_column(
        Integer, ForeignKey("distritos.id_distrito"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
