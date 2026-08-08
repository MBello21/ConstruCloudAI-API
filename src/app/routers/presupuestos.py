from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.presupuestos import PresupuestoCompletoResponse, PresupuestoCreadoResponse, ActualizarPresupuesto
from ..schemas.presupuestos_ia import SolicitudIAPresupuesto
from ..services.presupuesto_service import (
    crear_presupuesto_con_rag,
    get_metricas,
    get_presupuesto_by_id,
    listar_presupuestos,
    actualizar_presupuesto,
    eliminar_presupuesto,
)


router = APIRouter()


@router.post("/ia-rag")
async def crear_presupuesto(
    solicitud: SolicitudIAPresupuesto, db: Session = Depends(get_db)
):
    try:
        datos_respuesta = crear_presupuesto_con_rag(
            db=db,
            titulo=solicitud.titulo,
            descripcion=solicitud.descripcion,
            materiales_por_cliente=solicitud.materiales_por_cliente
        )
        return PresupuestoCreadoResponse.model_validate(datos_respuesta)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en la coherencia del presupuesto generado: {str(e)}. "
            f"La IA generó datos con inconsistencias aritméticas. "
            f"Por favor, intenta de nuevo con una descripción más detallada."
        )
    except Exception as e:
        db.rollback()
        print(f"❌ Error en la persistencia de datos: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error guardando presupuesto en BD: {str(e)}",
        )


@router.get('/metricas')
async def get_metricas_endpoint(db: Session = Depends(get_db)):
    return get_metricas(db)


@router.get('/{presupuesto_id}')
def obtener_presupuesto(
    presupuesto_id: int,
    db: Session = Depends(get_db)
):
    try:
        presupuesto = get_presupuesto_by_id(db, presupuesto_id)
        return PresupuestoCompletoResponse.model_validate(presupuesto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get('')
async def listar_presupuestos_endpoint(
    skip: int = 0,
    limit: int = 10,
    estado: str = None,
    db: Session = Depends(get_db)
):
    return listar_presupuestos(db, skip, limit, estado)


@router.put('/{presupuesto_id}')
async def actualizar_presupuesto_endpoint(
    presupuesto_id: int,
    datos: ActualizarPresupuesto,
    db: Session = Depends(get_db)
):
    try:
        return actualizar_presupuesto(db, presupuesto_id, datos)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete('/{presupuesto_id}')
async def eliminar_presupuesto_endpoint(
    presupuesto_id: int,
    db: Session = Depends(get_db)
):
    try:
        return eliminar_presupuesto(db, presupuesto_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
