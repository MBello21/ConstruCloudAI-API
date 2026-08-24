from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING:
    from .user import Users
    from .presupuestos import Presupuestos
    from .clientes import Clientes


class Empresa(Base):
    __tablename__ = 'empresa'

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(255), nullable=True)
    direccion_fiscal: Mapped[str] = mapped_column(String(255), nullable=True)
    documento: Mapped[str] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)
    web: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    users: Mapped[list["Users"]] = relationship(
        "Users",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
    presupuestos: Mapped[list["Presupuestos"]] = relationship(
        "Presupuestos",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
    clientes: Mapped[list["Clientes"]] = relationship(
        "Clientes",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
