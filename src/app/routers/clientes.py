from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.clientes import ClienteCreate, ClienteResponse
from ..services.cliente_service import (
    get_clientes,
    get_cliente_by_id,
    create_cliente,
    update_cliente,
    delete_cliente,
)

router = APIRouter()


@router.post("")
def crear_cliente_endpoint(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    try:
        cliente = create_cliente(db, cliente_data)
        return ClienteResponse.model_validate(cliente)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando cliente: {str(e)}"
        )


@router.get("")
def listar_clientes_endpoint(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    clientes = get_clientes(db, skip, limit)
    return [ClienteResponse.model_validate(cliente) for cliente in clientes]


@router.get("/{cliente_id}")
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = get_cliente_by_id(db, cliente_id)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    return ClienteResponse.model_validate(cliente)


@router.delete("/{cliente_id}")
def eliminar_cliente_endpoint(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    eliminado = delete_cliente(db, cliente_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return {"eliminado": True}


@router.put("/{cliente_id}")
def actualizar_cliente_endpoint(cliente_id: int, cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = update_cliente(db, cliente_id, cliente_data)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return ClienteResponse.model_validate(cliente)
