from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class PresupuestoResumen(BaseModel):
    id: int
    codigo: str
    titulo: str
    total: float
    estado: str

    model_config = ConfigDict(from_attributes=True)


class ClienteResponse(BaseModel):
    id: int
    nombre_cliente: str
    direccion: Optional[str] = None
    poblacion: str
    telefono: str
    email: Optional[str] = None
    presupuestos: List[PresupuestoResumen] = []

    model_config = ConfigDict(from_attributes=True)


class ClienteCreate(BaseModel):
    nombre_cliente: str
    direccion: Optional[str] = None
    poblacion: str
    telefono: str
    email: Optional[str] = None
