from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import Users
from ..schemas.auth import (
    CreateUserEmpresaRequest,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UpdateUserRequest,
    UpdateUserRolRequest,
    UserResponse,
)
from ..services.auth_service import (
    autenticar_usuario,
    crear_token,
    get_current_user,
    registrar_usuario,
    registrar_usuario_empresa,
)
from ..services.user_service import update_user

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup_endpoint(datos: SignupRequest, db: Session = Depends(get_db)):
    try:
        user = registrar_usuario(
            db, datos.email, datos.password, datos.nombre_completo
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    access_token = crear_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def me_endpoint(usuario: Users = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado. Requiere Bearer token."""
    return usuario


@router.put("/me", response_model=UserResponse)
def actualizar_me_endpoint(
    datos: UpdateUserRequest,
    usuario: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza los datos de empresa del usuario autenticado.

    Solo se modifican los campos presentes en el body: los que no se envían
    conservan su valor actual. Requiere Bearer token.
    """
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        return usuario

    actualizado = update_user(db, usuario.id, cambios)

    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return actualizado


@router.post(
    "/usuarios",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_usuario_empresa_endpoint(
    datos: CreateUserEmpresaRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un usuario dentro de la empresa del admin autenticado."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede crear usuarios",
        )

    try:
        usuario = registrar_usuario_empresa(
            db,
            datos.email,
            datos.password,
            datos.nombre_completo,
            current_user.empresa_id,
            datos.rol,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return usuario


@router.get("/usuarios", response_model=List[UserResponse])
def listar_usuarios_empresa_endpoint(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los usuarios de la empresa del admin autenticado."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede listar usuarios",
        )

    return (
        db.query(Users)
        .filter(Users.empresa_id == current_user.empresa_id)
        .all()
    )


@router.delete("/usuarios/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario_empresa_endpoint(
    user_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un usuario de la empresa del admin autenticado."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede eliminar usuarios",
        )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta",
        )

    usuario = (
        db.query(Users)
        .filter(
            Users.id == user_id,
            Users.empresa_id == current_user.empresa_id,
        )
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    db.delete(usuario)
    db.commit()


@router.put("/usuarios/{user_id}", response_model=UserResponse)
def actualizar_rol_usuario_empresa_endpoint(
    user_id: int,
    datos: UpdateUserRolRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el rol de un usuario de la empresa del admin autenticado."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede cambiar roles",
        )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes cambiar tu propio rol",
        )

    usuario = (
        db.query(Users)
        .filter(
            Users.id == user_id,
            Users.empresa_id == current_user.empresa_id,
        )
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    usuario.rol = datos.rol
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
def login_endpoint(credenciales: LoginRequest, db: Session = Depends(get_db)):
    user = autenticar_usuario(db, credenciales.email, credenciales.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = crear_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token)
