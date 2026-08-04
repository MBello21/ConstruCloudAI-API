from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.detalles import Detalles
from ..schemas.detalles import DetalleCreate, DetalleResponse, DetalleUpdate

router = APIRouter()


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


@router.post("", response_model=DetalleResponse, status_code=status.HTTP_201_CREATED)
def crear_detalle(detalle: DetalleCreate, db: Session = Depends(get_db)):
    nuevo_detalle = Detalles(**detalle.model_dump())
    nuevo_detalle.subtotal = _calcular_subtotal_detalle(
        nuevo_detalle.cantidad, nuevo_detalle.precio_unitario
    )
    nuevo_detalle.generado_por_ia = nuevo_detalle.generado_por_ia or False


    nuevo_detalle.precio_confirmado = nuevo_detalle.precio_confirmado or False
    nuevo_detalle.es_externo = nuevo_detalle.es_externo or False

    db.add(nuevo_detalle)
    db.flush()  # Carga relaciones para acceder al presupuesto

    _recalcular_presupuesto(nuevo_detalle.capitulo.presupuesto)

    db.commit()
    db.refresh(nuevo_detalle)
    return nuevo_detalle


@router.get("", response_model=List[DetalleResponse])
def listar_detalles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    detalles = db.query(Detalles).offset(skip).limit(limit).all()
    return detalles


@router.get("/{detalle_id}", response_model=DetalleResponse)
def obtener_detalle(detalle_id: int, db: Session = Depends(get_db)):
    detalle = db.query(Detalles).filter(Detalles.id == detalle_id).first()

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle no encontrado"
        )

    return detalle


@router.put("/{detalle_id}", response_model=DetalleResponse)
def actualizar_detalle(detalle_id: int, datos: DetalleUpdate, db: Session = Depends(get_db)):
    detalle = db.query(Detalles).filter(Detalles.id == detalle_id).first()

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle no encontrado"
        )

    datos_actualizados = datos.model_dump(exclude_unset=True)
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


@router.delete("/{detalle_id}")
def eliminar_detalle(detalle_id: int, db: Session = Depends(get_db)):
    detalle = db.query(Detalles).filter(Detalles.id == detalle_id).first()

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle no encontrado"
        )

    presupuesto = detalle.capitulo.presupuesto
    db.delete(detalle)
    db.flush()

    _recalcular_presupuesto(presupuesto)

    db.commit()
    return {"eliminado": True}
