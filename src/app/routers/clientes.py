from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.clientes import Clientes
from ..schemas.clientes import ClienteCreate, ClienteResponse

router = APIRouter()


@router.post("")
def crear_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = Clientes(**cliente_data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return ClienteResponse.model_validate(cliente)


@router.get("")
def listar_clientes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    clientes = db.query(Clientes).offset(skip).limit(limit).all()

    return [ClienteResponse.model_validate(cliente) for cliente in clientes]


@router.get("/{cliente_id}")
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    return ClienteResponse.model_validate(cliente)


@router.delete("/{cliente_id}")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()

    return {"eliminado": True}


@router.put("/{cliente_id}")
def actualizar_cliente(cliente_id: int, cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    datos = cliente_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return ClienteResponse.model_validate(cliente)
