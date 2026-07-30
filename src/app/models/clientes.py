from sqlalchemy import func, String, Text, ForeignKey, Integer, Numeric, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from ..database import Base
from .presupuestos import Presupuestos


class Clientes(Base):
    __tablename__ = 'clientes'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_cliente: Mapped[str] = mapped_column(Text, nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=True)
    poblacion: Mapped[str] = mapped_column(String(400), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(300), nullable=True)
    presupuestos: Mapped[list["Presupuestos"]] = relationship(
        "Presupuestos", back_populates="cliente")
