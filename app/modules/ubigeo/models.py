from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Departamento(Base):
    __tablename__ = "departamentos"

    id_departamento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Provincia(Base):
    __tablename__ = "provincias"

    id_provincia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_departamento: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id_departamento"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Distrito(Base):
    __tablename__ = "distritos"

    id_distrito: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_provincia: Mapped[int] = mapped_column(
        Integer, ForeignKey("provincias.id_provincia"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class TipoDocumento(Base):
    __tablename__ = "tipos_documento"

    id_tipo_documento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    abreviatura: Mapped[str] = mapped_column(String(10), nullable=False)
