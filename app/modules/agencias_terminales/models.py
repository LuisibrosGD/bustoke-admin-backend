from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgenciaTerminal(Base):
    __tablename__ = "agencias_terminales"

    id_agencia_terminal: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_agencia: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id_agencia"), nullable=False
    )
    id_terminal: Mapped[int] = mapped_column(
        Integer, ForeignKey("terminales.id_terminal"), nullable=False
    )
    nro_counter_oficina: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_agencia", "id_terminal", name="uq_agencia_terminal"),
    )
