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
    codigo: str | None = None
    nombre_cliente: str
    direccion: Optional[str] = None
    poblacion: str
    telefono: str
    email: Optional[str] = None
    estado: Optional[str] = "Activo"
    tipo: Optional[str] = "Empresa"
    cif: Optional[str] = None
    notas: Optional[str] = None
    presupuestos: List[PresupuestoResumen] = []

    model_config = ConfigDict(from_attributes=True)


class ClienteCreate(BaseModel):
    nombre_cliente: str
    direccion: Optional[str] = None
    poblacion: str
    telefono: str
    email: Optional[str] = None
    estado: Optional[str] = "Activo"
    tipo: Optional[str] = "Empresa"
    cif: Optional[str] = None
    notas: Optional[str] = None


class ClienteUpdate(BaseModel):
    nombre_cliente: Optional[str] = None
    direccion: Optional[str] = None
    poblacion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    estado: Optional[str] = None
    tipo: Optional[str] = None
    cif: Optional[str] = None
    notas: Optional[str] = None
