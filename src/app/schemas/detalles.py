from pydantic import BaseModel
from typing import List, Optional


class DetalleCreate(BaseModel):
    capitulo_id: int
    numero: int
    descripcion: str
    unidad: str
    cantidad: float
    precio_unitario: float
    subtotal: float = 0.0


class DetalleUpdate(BaseModel):
    descripcion: str | None = None
    unidad: str | None = None
    cantidad: float | None = None
    precio_unitario: float | None = None


class DetalleResponse(BaseModel):
    id: int
    capitulo_id: int
    numero: int
    descripcion: str
    unidad: str
    cantidad: float
    precio_unitario: float
    subtotal: float
    generado_por_ia: Optional[bool] = None

    class Config:
        from_attributes = True  # Permite mapear directamente desde modelos de SQLAlchemy
