from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.capitulos import Capitulos
from ..schemas.capitulos import CapituloUpdate, CapituloCreate, CapituloResponse


router = APIRouter()


@router.post("", response_model=CapituloResponse, status_code=status.HTTP_201_CREATED)
def crear_capitulo(capitulo: CapituloCreate, db: Session = Depends(get_db)):
    nuevo_capitulo = Capitulos(**capitulo.model_dump())
    db.add(nuevo_capitulo)
    db.commit()
    db.refresh(nuevo_capitulo)
    return nuevo_capitulo


@router.get("", response_model=List[CapituloResponse])
def listar_capitulos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    capitulos = db.query(Capitulos).offset(skip).limit(limit).all()
    return capitulos


@router.get("/{capitulo_id}", response_model=CapituloResponse)
def obtener_capitulo(capitulo_id: int, db: Session = Depends(get_db)):
    capitulo = db.query(Capitulos).filter(Capitulos.id == capitulo_id).first()

    if not capitulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capitulo no encontrado"
        )

    return capitulo


@router.put("/{capitulo_id}", response_model=CapituloResponse)
def actualizar_capitulo(capitulo_id: int, datos: CapituloUpdate, db: Session = Depends(get_db)):
    capitulo = db.query(Capitulos).filter(Capitulos.id == capitulo_id).first()

    if not capitulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capitulo no encontrado"
        )

    datos_actualizados = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizados.items():
        setattr(capitulo, campo, valor)

    db.commit()
    db.refresh(capitulo)

    return capitulo


@router.delete("/{capitulo_id}")
def eliminar_capitulo(capitulo_id: int, db: Session = Depends(get_db)):
    capitulo = db.query(Capitulos).filter(Capitulos.id == capitulo_id).first()

    if not capitulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capitulo no encontrado"
        )

    presupuesto = capitulo.presupuesto
    db.delete(capitulo)
    db.flush()

    subtotal = sum(
        d.subtotal or 0
        for cap in presupuesto.capitulos
        for d in cap.detalles
    )
    presupuesto.subtotal = subtotal
    presupuesto.total = subtotal * (1 + (presupuesto.iva or 21) / 100)

    db.commit()
    return {"eliminado": True}
