from pydantic import BaseModel
from typing import List, Optional


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
    codigo:str
    titulo: str
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
    total_capitulos_creados: int
    referencias_usadas: int
    similitud_promedio: float
    
