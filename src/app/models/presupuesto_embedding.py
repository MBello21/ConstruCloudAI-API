from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import func, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from ..database import Base

if TYPE_CHECKING:
    from .presupuestos import Presupuestos


class PresupuestoEmbedding(Base):
    __tablename__ = 'presupuestos_embeddings'

    id: Mapped[int] = mapped_column(primary_key=True)
    presupuesto_id: Mapped[int] = mapped_column(
        ForeignKey('presupuestos.id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )
    presupuesto: Mapped['Presupuestos'] = relationship(
        'Presupuestos',
        back_populates='embedding'
    )
    contenido_indexado: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(
        Vector(384), nullable=False, index=True)
    modelo_embedding: Mapped[str] = mapped_column(
        String(255),
        default='sentence-transformers/all-MiniLM-L6-v2'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<PresupuestoEmbedding(presupuesto_id={self.presupuesto_id})>"
