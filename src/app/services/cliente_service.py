from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.clientes import Clientes
from ..schemas.clientes import ClienteCreate, ClienteUpdate


def get_clientes(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[Clientes]:
    """Lista clientes con paginación."""
    return db.query(Clientes).offset(skip).limit(limit).all()


def get_clientes_listados(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    estado: str = None
) -> List[Clientes]:
    """Lista clientes con paginación."""
    query = db.query(Clientes)

    if estado and estado != 'Todos':
        query = query.filter(Clientes.estado == estado)

    total = query.count()
    clientes = query.order_by(Clientes.id.desc()).offset(
        skip).limit(limit).all()

    return {
        "total": total,
        "clientes": [{
            "id": c.id,
            "nombre_cliente": c.nombre_cliente,
            "telefono": c.telefono,
            "email": c.email,
            "direccion": c.direccion,
            "poblacion": c.poblacion,
            "estado": c.estado,
            "tipo": c.tipo,
            "cif": c.cif,
        }
            for c in clientes
        ]
    }


def get_cliente_by_id(db: Session, cliente_id: int) -> Optional[Clientes]:
    """Obtiene un cliente por ID. Retorna None si no existe."""
    return db.query(Clientes).filter(Clientes.id == cliente_id).first()


def create_cliente(db: Session, data: ClienteCreate) -> Clientes:
    """Crea un nuevo cliente."""
    cliente = Clientes(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def update_cliente(
    db: Session,
    cliente_id: int,
    data: ClienteUpdate
) -> Optional[Clientes]:
    """Actualiza un cliente. Retorna None si no existe."""
    cliente = get_cliente_by_id(db, cliente_id)

    if not cliente:
        return None

    datos = data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente


def delete_cliente(db: Session, cliente_id: int) -> bool:
    """Elimina un cliente. Retorna True si se eliminó."""
    cliente = get_cliente_by_id(db, cliente_id)

    if not cliente:
        return False

    db.delete(cliente)
    db.commit()
    return True
