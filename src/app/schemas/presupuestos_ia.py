from pydantic import BaseModel

class SolicitudIAPresupuesto(BaseModel):
  titulo: str = "Presupuesto Generado por IA"
  descripcion: str