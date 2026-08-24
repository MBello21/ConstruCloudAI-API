from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.detalles import Detalles
from ..schemas.detalles import DetalleCreate, DetalleUpdate


def _calcular_subtotal_detalle(cantidad, precio_unitario) -> Decimal:
    """Calcula el subtotal asegurando operandos de tipo Decimal."""
    cant = Decimal(str(cantidad)) if cantidad is not None else Decimal("0")
    precio = Decimal(str(precio_unitario)
                     ) if precio_unitario is not None else Decimal("0")
    return cant * precio


def _recalcular_presupuesto(presupuesto):
    """Recalcula subtotal y total del presupuesto en tipo Decimal."""
    subtotal = sum(
        Decimal(str(d.subtotal)) if d.subtotal is not None else Decimal("0")
        for cap in presupuesto.capitulos
        for d in cap.detalles
    )
    iva = Decimal(str(presupuesto.iva)
                  ) if presupuesto.iva is not None else Decimal("21")

    presupuesto.subtotal = subtotal
    presupuesto.total = subtotal * (Decimal("1") + (iva / Decimal("100")))


def get_detalles(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[Detalles]:
    """Lista detalles con paginación."""
    return db.query(Detalles).offset(skip).limit(limit).all()


def get_detalle_by_id(db: Session, detalle_id: int) -> Optional[Detalles]:
    """Obtiene un detalle por ID. Retorna None si no existe."""
    return db.query(Detalles).filter(Detalles.id == detalle_id).first()


def create_detalle(db: Session, data: DetalleCreate) -> Detalles:
    """Crea un nuevo detalle y recalcula el presupuesto."""
    nuevo_detalle = Detalles(**data.model_dump())
    nuevo_detalle.subtotal = _calcular_subtotal_detalle(
        nuevo_detalle.cantidad, nuevo_detalle.precio_unitario
    )
    nuevo_detalle.generado_por_ia = nuevo_detalle.generado_por_ia or False
    nuevo_detalle.precio_confirmado = nuevo_detalle.precio_confirmado or False
    nuevo_detalle.es_externo = nuevo_detalle.es_externo or False

    db.add(nuevo_detalle)
    db.flush()

    _recalcular_presupuesto(nuevo_detalle.capitulo.presupuesto)

    db.commit()
    db.refresh(nuevo_detalle)
    return nuevo_detalle


def update_detalle(
    db: Session,
    detalle_id: int,
    data: DetalleUpdate
) -> Optional[Detalles]:
    """Actualiza un detalle y recalcula el presupuesto. Retorna None si no existe."""
    detalle = get_detalle_by_id(db, detalle_id)

    if not detalle:
        return None

    datos_actualizados = data.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizados.items():
        setattr(detalle, campo, valor)

    detalle.subtotal = _calcular_subtotal_detalle(
        detalle.cantidad, detalle.precio_unitario
    )
    db.flush()

    _recalcular_presupuesto(detalle.capitulo.presupuesto)
    db.commit()
    db.refresh(detalle)

    return detalle


def delete_detalle(db: Session, detalle_id: int) -> bool:
    """Elimina un detalle y recalcula el presupuesto. Retorna True si se eliminó."""
    detalle = get_detalle_by_id(db, detalle_id)

    if not detalle:
        return False

    presupuesto = detalle.capitulo.presupuesto
    db.delete(detalle)
    db.flush()

    _recalcular_presupuesto(presupuesto)

    db.commit()
    return True
