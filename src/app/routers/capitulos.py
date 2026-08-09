from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas.capitulos import CapituloUpdate, CapituloCreate, CapituloResponse
from ..services import capitulo_service


router = APIRouter()


@router.post("", response_model=CapituloResponse, status_code=status.HTTP_201_CREATED)
def crear_capitulo(capitulo: CapituloCreate, db: Session = Depends(get_db)):
    return capitulo_service.create_capitulo(db, capitulo)


@router.get("", response_model=List[CapituloResponse])
def listar_capitulos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return capitulo_service.get_capitulos(db, skip, limit)


@router.get("/{capitulo_id}", response_model=CapituloResponse)
def obtener_capitulo(capitulo_id: int, db: Session = Depends(get_db)):
    capitulo = capitulo_service.get_capitulo_by_id(db, capitulo_id)
    if not capitulo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capitulo no encontrado")
    return capitulo


@router.put("/{capitulo_id}", response_model=CapituloResponse)
def actualizar_capitulo(capitulo_id: int, datos: CapituloUpdate, db: Session = Depends(get_db)):
    capitulo = capitulo_service.update_capitulo(db, capitulo_id, datos)
    if not capitulo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capitulo no encontrado")
    return capitulo


@router.delete("/{capitulo_id}")
def eliminar_capitulo(capitulo_id: int, db: Session = Depends(get_db)):
    eliminado = capitulo_service.delete_capitulo(db, capitulo_id)
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capitulo no encontrado")
    return {"eliminado": True}
