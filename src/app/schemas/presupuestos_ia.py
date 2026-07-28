from pydantic import BaseModel
from typing import Optional

class SolicitudIAPresupuesto(BaseModel):
  titulo: str = "Presupuesto Generado por IA"
  descripcion: str
  materiales_por_cliente: Optional[bool] = False

  class Config:
    json_schema_extra = {
      "example": {
        "titulo": "Reforma baño",
        "descripcion": "Baño 6m² completo con azulejos blancos",
        "materiales_por_cliente": False
      }
    }