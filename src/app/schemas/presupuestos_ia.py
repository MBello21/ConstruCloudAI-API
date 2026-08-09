from pydantic import BaseModel, Field
from typing import List, Optional


class SolicitudIAPresupuesto(BaseModel):
    """Petición del usuario para que la IA genere una propuesta de presupuesto."""

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


class DetalleEstructura(BaseModel):
    """
    Partida dentro de un capítulo.

    No reutiliza `DetalleCreate` porque ese schema exige `capitulo_id`, que aún
    no existe cuando la estructura viaja anidada (el capítulo todavía no está
    persistido).
    """

    numero: Optional[int] = None
    descripcion: str
    unidad: str = "ud"
    cantidad: float = 0.0
    precio_unitario: float = 0.0
    subtotal: float = 0.0
    generado_por_ia: bool = True
    precio_confirmado: bool = False
    es_externo: bool = False


class CapituloEstructura(BaseModel):
    """
    Capítulo con sus partidas anidadas.

    Mismo motivo que en `DetalleEstructura`: `CapituloCreate` exige
    `presupuesto_id`, inexistente antes de persistir.
    """

    numero: Optional[int] = None
    nombre: str
    orden: Optional[int] = None
    subtotal: float = 0.0
    detalles: List[DetalleEstructura] = []


class EstructuraPresupuesto(BaseModel):
    """
    Estructura completa de un presupuesto (cabecera + capítulos + detalles).

    Es lo que devuelve `POST /ia-rag` (sin persistir) y lo que espera
    `POST /` para persistir tras la revisión del usuario.
    """

    titulo: str
    descripcion: Optional[str] = None
    cliente_id: Optional[int] = None
    estado: Optional[str] = None
    condiciones_pago: Optional[str] = None
    validez_dias: int = 30
    subtotal: float = 0.0
    iva: float = 21.0
    total: float = 0.0
    capitulos: List[CapituloEstructura] = []

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Reforma baño",
                "descripcion": "Baño 6m² completo con azulejos blancos",
                "condiciones_pago": "25% depósito, 50% certificaciones, 25% fin de obra",
                "validez_dias": 30,
                "subtotal": 5036.00,
                "iva": 21.0,
                "total": 6093.56,
                "capitulos": [
                    {
                        "numero": 1,
                        "nombre": "TRABAJOS PREVIOS Y DEMOLICIONES",
                        "orden": 1,
                        "subtotal": 308.00,
                        "detalles": [
                            {
                                "numero": 1,
                                "descripcion": "Demolición de alicatado en paredes",
                                "unidad": "m2",
                                "cantidad": 22.0,
                                "precio_unitario": 14.0,
                                "subtotal": 308.00,
                                "generado_por_ia": True,
                                "precio_confirmado": False,
                                "es_externo": False,
                            }
                        ],
                    }
                ],
            }
        }


class ReferenciaRAG(BaseModel):
    """Presupuesto similar usado como contexto para la generación."""

    presupuesto_id: int
    titulo: str
    total: float
    iva: float
    similitud: float


class PresupuestoGeneradoResponse(BaseModel):
    """
    Respuesta de `POST /ia-rag`: propuesta NO persistida.

    El frontend revisa/edita `presupuesto` y lo reenvía a `POST /`.
    """

    presupuesto: EstructuraPresupuesto
    referencias_usadas: int = 0
    similitud_promedio: float = 0.0
    contexto_usado: List[ReferenciaRAG] = Field(default_factory=list)
    persistido: bool = False
