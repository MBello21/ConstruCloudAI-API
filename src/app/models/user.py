from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(255), nullable=True)
    direccion_fiscal: Mapped[str] = mapped_column(String(255), nullable=True)
    documento: Mapped[str] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)
    web: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
