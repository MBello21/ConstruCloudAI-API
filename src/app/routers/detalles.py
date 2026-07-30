from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.detalles import Detalles
from ..schemas.detalles import DetalleUpdate, DetalleCreate, DetalleResponse


router = APIRouter(prefix="/detalles")


@router.post("", response_model=DetalleResponse, status_code=status.HTTP_201_CREATED)
def crear_detalle(detalle: DetalleCreate, db: Session = Depends(get_db)):
    nuevo_detalle = Detalles(**detalle.model_dump())
    db.add(nuevo_detalle)
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

    db.delete(detalle)
    db.commit()

    return {"eliminado": True}
