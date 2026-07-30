from pydantic import BaseModel
from typing import List, Optional


class CapituloCreate(BaseModel):
    presupuesto_id: str
    numero: int
    nombre: str
    orden: int = 0


class CapituloUpdate(BaseModel):
    nombre: str | None = None
    numero: int | None = None
    orden: int | None = None


class CapituloResponse(BaseModel):
    id: int
    presupuesto_id: int
    numero:int
    nombre:str
    orden: int
    
    class Config:
        from_attributes = True