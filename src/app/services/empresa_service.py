from typing import Optional
from sqlalchemy.orm import Session

from ..models.empresa import Empresa


def get_empresa_by_id(db: Session, empresa_id: int) -> Optional[Empresa]:
    """Obtiene una empresa por ID. Retorna None si no existe."""
    return db.query(Empresa).filter(Empresa.id == empresa_id).first()


def update_empresa(db: Session, empresa_id: int, data: dict) -> Optional[Empresa]:
    """Actualiza una empresa. Retorna None si no existe."""
    empresa = get_empresa_by_id(db, empresa_id)

    if not empresa:
        return None

    for campo, valor in data.items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return empresa
