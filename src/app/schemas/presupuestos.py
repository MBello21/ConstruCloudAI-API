from pydantic import BaseModel
from typing import List, Optional


class ClienteBasico(BaseModel):
    id: int
    nombre_cliente: str

    class Config:
        from_attributes = True


class ActualizarPresupuesto(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    estado: str | None = None
    cliente_id: int | None = None
    validez_dias: int | None = None
    condiciones_pago: str | None = None
    iva: float | None = None


class DetallePresupuestoResponse(BaseModel):
    id: int
    numero: int
    descripcion: str
    cantidad: float
    unidad: str
    precio_unitario: float
    subtotal: float
    generado_por_ia: Optional[bool] = None

    class Config:
        from_attributes = True  # Permite mapear directamente desde modelos de SQLAlchemy


class CapituloPresupuestoResponse(BaseModel):
    id: int
    numero: int
    nombre: str
    detalles: List[DetallePresupuestoResponse] = []

    class Config:
        from_attributes = True


class PresupuestoCompletoResponse(BaseModel):
    id: int
    cliente_id: Optional[int] = None
    codigo: str
    titulo: str
    condiciones_pago: str
    validez_dias: int
    descripcion: Optional[str] = None
    estado: str
    subtotal: float
    iva: float
    total: float
    capitulos: List[CapituloPresupuestoResponse] = []

    class Config:
        from_attributes = True


class PresupuestoCreadoResponse(BaseModel):
    mensaje: str
    presupuesto_id: int
    codigo: str
    cliente: Optional[ClienteBasico] = None
    total_capitulos_creados: int
    referencias_usadas: int
    similitud_promedio: float
