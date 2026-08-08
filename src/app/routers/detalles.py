from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.detalles import DetalleCreate, DetalleResponse, DetalleUpdate
from ..services.detalle_service import (
    get_detalles,
    get_detalle_by_id,
    create_detalle,
    update_detalle,
    delete_detalle,
)

router = APIRouter()


@router.post("", response_model=DetalleResponse, status_code=status.HTTP_201_CREATED)
def crear_detalle_endpoint(detalle: DetalleCreate, db: Session = Depends(get_db)):
    try:
        return create_detalle(db, detalle)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando detalle: {str(e)}"
        )


@router.get("", response_model=List[DetalleResponse])
def listar_detalles_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_detalles(db, skip, limit)


@router.get("/{detalle_id}", response_model=DetalleResponse)
def obtener_detalle(detalle_id: int, db: Session = Depends(get_db)):
    detalle = get_detalle_by_id(db, detalle_id)

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle no encontrado"
        )

    return detalle


@router.put("/{detalle_id}", response_model=DetalleResponse)
def actualizar_detalle_endpoint(detalle_id: int, datos: DetalleUpdate, db: Session = Depends(get_db)):
    detalle = update_detalle(db, detalle_id, datos)

    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle no encontrado"
        )

    return detalle


@router.delete("/{detalle_id}")
def eliminar_detalle_endpoint(detalle_id: int, db: Session = Depends(get_db)):
    eliminado = delete_detalle(db, detalle_id)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle no encontrado"
        )

    return {"eliminado": True}
