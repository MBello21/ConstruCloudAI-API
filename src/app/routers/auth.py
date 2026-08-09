from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import LoginRequest, SignupRequest, TokenResponse
from ..services.auth_service import (
    autenticar_usuario,
    crear_token,
    registrar_usuario,
)

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup_endpoint(datos: SignupRequest, db: Session = Depends(get_db)):
    try:
        user = registrar_usuario(db, datos.email, datos.password)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    access_token = crear_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=access_token)


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
