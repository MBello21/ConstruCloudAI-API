from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import Users
from ..schemas.empresa import EmpresaResponse, EmpresaUpdate
from ..services.auth_service import get_current_user
from ..services.empresa_service import get_empresa_by_id, update_empresa

router = APIRouter()


@router.get("", response_model=EmpresaResponse)
def obtener_empresa_endpoint(
    usuario: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve los datos de la empresa del usuario autenticado."""
    empresa = get_empresa_by_id(db, usuario.empresa_id)

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    return empresa


@router.put("", response_model=EmpresaResponse)
def actualizar_empresa_endpoint(
    datos: EmpresaUpdate,
    usuario: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza la empresa del usuario autenticado. Solo el rol admin puede hacerlo."""
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede modificar la empresa",
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        empresa = get_empresa_by_id(db, usuario.empresa_id)
    else:
        empresa = update_empresa(db, usuario.empresa_id, cambios)

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    return empresa
