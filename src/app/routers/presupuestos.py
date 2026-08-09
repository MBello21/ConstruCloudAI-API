from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.presupuestos import PresupuestoCompletoResponse, ActualizarPresupuesto
from ..schemas.presupuestos_ia import (
    SolicitudIAPresupuesto,
    EstructuraPresupuesto,
    PresupuestoGeneradoResponse,
)
from ..services.presupuesto_service import (
    generar_presupuesto_ia,
    crear_presupuesto_desde_estructura,
    get_metricas,
    get_presupuesto_by_id,
    listar_presupuestos,
    actualizar_presupuesto,
    eliminar_presupuesto,
)


router = APIRouter()


@router.post("/ia-rag", response_model=PresupuestoGeneradoResponse)
async def generar_presupuesto_ia_endpoint(
    solicitud: SolicitudIAPresupuesto, db: Session = Depends(get_db)
):
    """
    Genera una propuesta de presupuesto con IA + RAG. NO persiste nada.

    El frontend revisa/edita el JSON devuelto y lo envía a `POST /presupuestos/`
    para guardarlo.
    """
    try:
        datos_respuesta = generar_presupuesto_ia(db=db, solicitud=solicitud)
        return PresupuestoGeneradoResponse.model_validate(datos_respuesta)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en la coherencia del presupuesto generado: {str(e)}. "
            f"La IA generó datos con inconsistencias aritméticas. "
            f"Por favor, intenta de nuevo con una descripción más detallada."
        )
    except Exception as e:
        print(f"❌ Error generando presupuesto con IA: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generando presupuesto con IA: {str(e)}",
        )


@router.post(
    "",
    response_model=PresupuestoCompletoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_presupuesto(
    estructura: EstructuraPresupuesto, db: Session = Depends(get_db)
):
    try:
        presupuesto = crear_presupuesto_desde_estructura(
            db=db, datos=estructura)
        return PresupuestoCompletoResponse.model_validate(presupuesto)
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en la coherencia del presupuesto: {str(e)}",
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
