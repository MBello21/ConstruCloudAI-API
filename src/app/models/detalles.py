from sqlalchemy import func, String, Text, ForeignKey, Integer, Numeric, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime
from ..database import Base

if TYPE_CHECKING:
    from .capitulos import Capitulos


class Detalles(Base):

    __tablename__ = 'detalles'

    id: Mapped[int] = mapped_column(primary_key=True)
    capitulo_id: Mapped[int] = mapped_column(
        ForeignKey('capitulos.id'), nullable=True)
    capitulo: Mapped['Capitulos'] = relationship(
        'Capitulos', back_populates='detalles')
    numero: Mapped[int] = mapped_column(Integer)
    descripcion: Mapped[str] = mapped_column(Text)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    precio_unitario: Mapped[int] = mapped_column(
        Numeric, nullable=False, default=0)
    subtotal: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    generado_por_ia: Mapped[bool] = mapped_column(default=False)
    precio_confirmado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    es_externo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
