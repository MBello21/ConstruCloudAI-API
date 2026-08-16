from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import Users
from ..schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UpdateUserRequest,
    UserResponse,
)
from ..services.auth_service import (
    autenticar_usuario,
    crear_token,
    get_current_user,
    registrar_usuario,
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
