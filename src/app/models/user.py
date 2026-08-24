from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING:
    from .empresa import Empresa


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(
        ForeignKey("empresa.id"), nullable=True)
    empresa: Mapped["Empresa"] = relationship(
        "Empresa", back_populates="users")
    nombre_completo: Mapped[str] = mapped_column(String(255), nullable=True)
    cargo: Mapped[str] = mapped_column(String(255), nullable=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
