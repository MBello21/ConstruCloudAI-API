"""
Servicio de gestión de precios para presupuestos.

Soporta dos modalidades:
1. OBRA COMPLETA: Empresa aporta materiales + mano de obra
2. SOLO MANO DE OBRA: Cliente aporta materiales, empresa cobra colocación + auxiliares
"""

from typing import Dict, Optional
from enum import Enum


class ModalidadTrabajo(str, Enum):
    """Modalidades de trabajo soportadas."""
    OBRA_COMPLETA = "OBRA COMPLETA"
    SOLO_MANO_OBRA = "SOLO MANO DE OBRA / MATERIALES APORTADOS POR CLIENTE"


class PricingService:
    """
    Servicio de gestión de precios según modalidad de trabajo.

    Mantiene tablas de precios para ambas modalidades y proporciona métodos
    para consultar rangos de precios realistas según el tipo de trabajo.
    """

    # TABLA DE PRECIOS - OBRA COMPLETA (Material + Instalación)
    PRECIOS_OBRA_COMPLETA = {
        "alicatado": {
            "unidad": "m2",
            "rango_min": 30.0,
            "rango_max": 55.0,
            "descripcion": "Alicatado material + instalación"
        },
        "solado": {
            "unidad": "m2",
            "rango_min": 30.0,
            "rango_max": 50.0,
            "descripcion": "Solado material + instalación"
        },
        "rodapie": {
            "unidad": "m",
            "rango_min": 8.0,
            "rango_max": 15.0,
            "descripcion": "Rodapié material + instalación"
        },
        "inodoro": {
            "unidad": "ud",
            "rango_min": 550.0,
            "rango_max": 800.0,
            "descripcion": "Inodoro suministro + instalación"
        },
        "lavamanos": {
            "unidad": "ud",
            "rango_min": 250.0,
            "rango_max": 350.0,
            "descripcion": "Lavamanos suministro + instalación"
        },
        "plato_ducha": {
            "unidad": "ud",
            "rango_min": 350.0,
            "rango_max": 500.0,
            "descripcion": "Plato de ducha suministro + instalación"
        },
        "mampara": {
            "unidad": "ud",
            "rango_min": 300.0,
            "rango_max": 600.0,
            "descripcion": "Mampara suministro + instalación"
        },
        "encimera": {
            "unidad": "m2",
            "rango_min": 150.0,
            "rango_max": 400.0,
            "descripcion": "Encimera suministro + instalación"
        },
        "pintura": {
            "unidad": "m2",
            "rango_min": 6.0,
            "rango_max": 10.0,
            "descripcion": "Pintura material + aplicación"
        },
    }

    # TABLA DE PRECIOS - SOLO MANO DE OBRA (Colocación + Auxiliares)
    PRECIOS_SOLO_MANO_OBRA = {
        "alicatado": {
            "unidad": "m2",
            "rango_min": 18.0,
            "rango_max": 24.0,
            "descripcion": "Colocación alicatado aportado + auxiliares"
        },
        "solado": {
            "unidad": "m2",
            "rango_min": 18.0,
            "rango_max": 24.0,
            "descripcion": "Colocación solado aportado + auxiliares"
        },
        "rodapie": {
            "unidad": "m",
            "rango_min": 5.0,
            "rango_max": 8.0,
            "descripcion": "Colocación rodapié aportado + auxiliares"
        },
        "inodoro": {
            "unidad": "ud",
            "rango_min": 70.0,
            "rango_max": 120.0,
            "descripcion": "Instalación inodoro aportado"
        },
        "lavamanos": {
            "unidad": "ud",
            "rango_min": 60.0,
            "rango_max": 100.0,
            "descripcion": "Instalación lavamanos aportado"
        },
        "plato_ducha": {
            "unidad": "ud",
            "rango_min": 100.0,
            "rango_max": 180.0,
            "descripcion": "Instalación plato ducha aportado"
        },
        "mampara": {
            "unidad": "ud",
            "rango_min": 120.0,
            "rango_max": 200.0,
            "descripcion": "Instalación mampara aportada"
        },
        "encimera": {
            "unidad": "m2",
            "rango_min": 120.0,
            "rango_max": 200.0,
            "descripcion": "Montaje encimera aportada"
        },
        "pintura": {
            "unidad": "m2",
            "rango_min": 3.0,
            "rango_max": 6.0,
            "descripcion": "Aplicación pintura (material propio)"
        },
    }

    @classmethod
    def obtener_rango_precio(
        cls,
        concepto: str,
        modalidad: ModalidadTrabajo = ModalidadTrabajo.OBRA_COMPLETA,
    ) -> Optional[Dict]:
        """
        Obtiene el rango de precios para un concepto dado.

        Args:
            concepto: Tipo de trabajo (ej. "alicatado", "inodoro", "pintura")
            modalidad: Modalidad de trabajo (OBRA_COMPLETA o SOLO_MANO_OBRA)

        Returns:
            Dict con estructura: {unidad, rango_min, rango_max, descripcion}
            None si el concepto no existe
        """
        tabla_precios = (
            cls.PRECIOS_OBRA_COMPLETA
            if modalidad == ModalidadTrabajo.OBRA_COMPLETA
            else cls.PRECIOS_SOLO_MANO_OBRA
        )

        return tabla_precios.get(concepto.lower())

    @classmethod
    def es_valido_precio(
        cls,
        concepto: str,
        precio_unitario: float,
        modalidad: ModalidadTrabajo = ModalidadTrabajo.OBRA_COMPLETA,
    ) -> bool:
        """
        Valida si un precio unitario está dentro de los rangos de mercado.

        Args:
            concepto: Tipo de trabajo
            precio_unitario: Precio a validar
            modalidad: Modalidad de trabajo

        Returns:
            True si el precio es válido, False si está fuera de rango
        """
        rango = cls.obtener_rango_precio(concepto, modalidad)
        if not rango:
            return True  # Si no hay registro, asumir válido

        return rango["rango_min"] <= precio_unitario <= rango["rango_max"]

    @classmethod
    def obtener_precio_medio(
        cls,
        concepto: str,
        modalidad: ModalidadTrabajo = ModalidadTrabajo.OBRA_COMPLETA,
    ) -> Optional[float]:
        """
        Obtiene el precio medio (promedio del rango) para un concepto.

        Args:
            concepto: Tipo de trabajo
            modalidad: Modalidad de trabajo

        Returns:
            Precio medio, None si concepto no existe
        """
        rango = cls.obtener_rango_precio(concepto, modalidad)
        if not rango:
            return None

        return (rango["rango_min"] + rango["rango_max"]) / 2

    @classmethod
    def listar_conceptos_disponibles(self) -> Dict[str, Dict]:
        """Devuelve la lista de conceptos disponibles con sus precios."""
        return {
            "OBRA_COMPLETA": self.PRECIOS_OBRA_COMPLETA,
            "SOLO_MANO_OBRA": self.PRECIOS_SOLO_MANO_OBRA,
        }

    @classmethod
    def describir_modalidad(
        cls, modalidad: ModalidadTrabajo = ModalidadTrabajo.OBRA_COMPLETA
    ) -> str:
        """Devuelve descripción textual de la modalidad."""
        if modalidad == ModalidadTrabajo.OBRA_COMPLETA:
            return (
                "Obra Completa: La empresa aporta y suministra todos los materiales. "
                "Precios incluyen material + mano de obra."
            )
        else:
            return (
                "Solo Mano de Obra: El cliente aporta los materiales. "
                "La empresa cobra solo colocación/instalación + materiales auxiliares de agarre."
            )
