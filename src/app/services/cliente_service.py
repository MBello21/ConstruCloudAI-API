from sqlalchemy.orm import joinedload
from typing import List, Optional
from sqlalchemy.orm import Session, subqueryload
import uuid

from ..models.clientes import Clientes
from ..schemas.clientes import ClienteCreate, ClienteUpdate


def _filtrar_por_empresa(query, empresa_id: Optional[int]):
    """Restringe la query a la empresa indicada (o a los registros sin empresa)."""
    if empresa_id is None:
        return query.filter(Clientes.empresa_id.is_(None))
    return query.filter(Clientes.empresa_id == empresa_id)


def get_clientes(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    empresa_id: Optional[int] = None
) -> List[Clientes]:
    query = _filtrar_por_empresa(db.query(Clientes), empresa_id)
    query = query.options(subqueryload(Clientes.presupuestos))
    return query.offset(skip).limit(limit).all()


def get_clientes_listados(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    estado: str = None,
    empresa_id: Optional[int] = None
) -> List[Clientes]:
    """Lista clientes de la empresa con paginación."""
    query = _filtrar_por_empresa(db.query(Clientes), empresa_id)

    if estado and estado != 'Todos':
        query = query.filter(Clientes.estado == estado)

    total = query.count()
    clientes = query.order_by(Clientes.id.desc()).options(
        subqueryload(Clientes.presupuestos)
    ).offset(skip).limit(limit).all()

    return {
        "total": total,
        "clientes": [{
            "id": c.id,
            "codigo": c.codigo,
            "nombre_cliente": c.nombre_cliente,
            "telefono": c.telefono,
            "email": c.email,
            "direccion": c.direccion,
            "poblacion": c.poblacion,
            "estado": c.estado,
            "tipo": c.tipo,
            "cif": c.cif,
            "num_presupuestos": len(c.presupuestos),
            "volumen": float(sum(p.total for p in c.presupuestos)),
        } for c in clientes]
    }


def get_cliente_by_id(
    db: Session,
    cliente_id: int,
    empresa_id: Optional[int] = None
) -> Optional[Clientes]:
    """Obtiene un cliente por ID dentro de la empresa. Retorna None si no existe o pertenece a otra empresa."""
    query = _filtrar_por_empresa(db.query(Clientes), empresa_id)
    return query.filter(Clientes.id == cliente_id).first()


def create_cliente(
    db: Session,
    data: ClienteCreate,
    empresa_id: Optional[int] = None
) -> Clientes:
    codigo = f"CLI-{uuid.uuid4().hex[:6].upper()}"
    cliente = Clientes(**data.model_dump(), codigo=codigo,
                       empresa_id=empresa_id)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def update_cliente(
    db: Session,
    cliente_id: int,
    data: ClienteUpdate,
    empresa_id: Optional[int] = None
) -> Optional[Clientes]:
    """Actualiza un cliente de la empresa. Retorna None si no existe o pertenece a otra empresa."""
    cliente = get_cliente_by_id(db, cliente_id, empresa_id)

    if not cliente:
        return None

    datos = data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente


def delete_cliente(
    db: Session,
    cliente_id: int,
    empresa_id: Optional[int] = None
) -> bool:
    """Elimina un cliente de la empresa. Retorna True si se eliminó."""
    cliente = get_cliente_by_id(db, cliente_id, empresa_id)

    if not cliente:
        return False

    db.delete(cliente)
    db.commit()
    return True
