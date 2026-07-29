<<<<<<< HEAD
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import func, String, Text, Numeric, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
import enum

if TYPE_CHECKING:
    from .capitulos import Capitulos
    from .presupuesto_embedding import PresupuestoEmbedding


class EstadoPresupuesto(str, enum.Enum):
    BORRADOR = "Borrador"
    ENVIADO = "Enviado"
    REVISION = "En Revisión"
    ACEPTADO = "Aprobado"
    RECHAZADO = "Rechazado"
    

class Presupuestos(Base):
    __tablename__ = 'presupuestos'

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text)
    estado: Mapped[EstadoPresupuesto] = mapped_column(
        SQLEnum(EstadoPresupuesto),
        default=EstadoPresupuesto.BORRADOR
    )
    subtotal: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    iva: Mapped[int] = mapped_column(Numeric, nullable=False, default=21.00)
    total: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    condiciones_pago: Mapped[str] = mapped_column(Text)
    validez_dias: Mapped[int] = mapped_column(Integer, default=30)

    contexto_rag: Mapped[str] = mapped_column(Text, nullable=True)

    embedding: Mapped["PresupuestoEmbedding"] = relationship(
        "PresupuestoEmbedding",
        back_populates="presupuesto",
        cascade="all, delete-orphan",
        uselist=False
    )
    capitulos: Mapped[list["Capitulos"]] = relationship(
        "Capitulos",
        back_populates="presupuesto",
        cascade="all, delete-orphan"
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
        return f"<Presupuestos(id={self.id}, codigo={self.codigo})>"
=======
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import func, String, Text, Numeric, Integer, DateTime, ForeignKey,  Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
import enum


if TYPE_CHECKING:
    from .capitulos import Capitulos
    from .presupuesto_embedding import PresupuestoEmbedding
    from .clientes import Clientes


class EstadoPresupuesto(str, enum.Enum):
    BORRADOR = "Borrador"
    ENVIADO = "Enviado"
    REVISION = "En Revisión"
    ACEPTADO = "Aprobado"
    RECHAZADO = "Rechazado"


class Presupuestos(Base):
    __tablename__ = 'presupuestos'

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey('clientes.id'), nullable=True)
    cliente: Mapped["Clientes"] = relationship(
        "Clientes", back_populates="presupuestos")
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text)
    estado: Mapped[EstadoPresupuesto] = mapped_column(
        SQLEnum(EstadoPresupuesto),
        default=EstadoPresupuesto.BORRADOR
    )
    subtotal: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    iva: Mapped[int] = mapped_column(Numeric, nullable=False, default=21.00)
    total: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    condiciones_pago: Mapped[str] = mapped_column(Text)
    validez_dias: Mapped[int] = mapped_column(Integer, default=30)

    contexto_rag: Mapped[str] = mapped_column(Text, nullable=True)

    embedding: Mapped["PresupuestoEmbedding"] = relationship(
        "PresupuestoEmbedding",
        back_populates="presupuesto",
        cascade="all, delete-orphan",
        uselist=False
    )
    capitulos: Mapped[list["Capitulos"]] = relationship(
        "Capitulos",
        back_populates="presupuesto",
        cascade="all, delete-orphan"
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
        return f"<Presupuestos(id={self.id}, codigo={self.codigo})>"
>>>>>>> 482b90c2a11552e1eac1cc13373dcabe016d702e
