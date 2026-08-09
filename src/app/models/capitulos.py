from sqlalchemy import func, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime
from ..database import Base

if TYPE_CHECKING:
    from .presupuestos import Presupuestos
    from .detalles import Detalles


class Capitulos(Base):

    __tablename__ = 'capitulos'

    id: Mapped[int] = mapped_column(primary_key=True)
    presupuesto_id: Mapped[int] = mapped_column(
        ForeignKey('presupuestos.id'), nullable=True)
    presupuesto: Mapped['Presupuestos'] = relationship(
        'Presupuestos', back_populates='capitulos')
    numero: Mapped[int] = mapped_column(Integer)
    nombre: Mapped[str] = mapped_column(String(300))
    detalles: Mapped[list["Detalles"]] = relationship(
        "Detalles",
        back_populates="capitulo",
        cascade="all, delete-orphan"
    )
    orden: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
