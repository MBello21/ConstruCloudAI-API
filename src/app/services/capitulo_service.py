from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.capitulos import Capitulos
from ..schemas.capitulos import CapituloCreate, CapituloUpdate


def get_capitulos(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[Capitulos]:
    """Lista capítulos con paginación."""
    return db.query(Capitulos).offset(skip).limit(limit).all()


def get_capitulo_by_id(db: Session, capitulo_id: int) -> Optional[Capitulos]:
    """Obtiene un capítulo por ID. Retorna None si no existe."""
    return db.query(Capitulos).filter(Capitulos.id == capitulo_id).first()


def create_capitulo(db: Session, data: CapituloCreate) -> Capitulos:
    """Crea un nuevo capítulo."""
    nuevo_capitulo = Capitulos(**data.model_dump())
    db.add(nuevo_capitulo)
    db.commit()
    db.refresh(nuevo_capitulo)
    return nuevo_capitulo


def update_capitulo(
    db: Session,
    capitulo_id: int,
    data: CapituloUpdate
) -> Optional[Capitulos]:
    """Actualiza un capítulo. Retorna None si no existe."""
    capitulo = get_capitulo_by_id(db, capitulo_id)

    if not capitulo:
        return None

    datos_actualizados = data.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizados.items():
        setattr(capitulo, campo, valor)

    db.commit()
    db.refresh(capitulo)

    return capitulo


def delete_capitulo(db: Session, capitulo_id: int) -> bool:
    """Elimina un capítulo y recalcula totales del presupuesto. Retorna True si se eliminó."""
    capitulo = get_capitulo_by_id(db, capitulo_id)

    if not capitulo:
        return False

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
    return True
