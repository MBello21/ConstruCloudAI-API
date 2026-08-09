import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import Users
from .user_service import (
    get_user_by_email,
    get_user_by_id,
    hash_password,
    verify_password,
)


ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = 480

security = HTTPBearer()


def _get_secret_key() -> str:
    """Lee la SECRET_KEY del entorno. Lanza RuntimeError si no está definida."""
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY no está definida en las variables de entorno."
        )
    return secret_key


def _get_expire_minutes() -> int:
    """Minutos de validez del token. Usa el valor por defecto si no es válido."""
    try:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", DEFAULT_EXPIRE_MINUTES))
    except ValueError:
        return DEFAULT_EXPIRE_MINUTES


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verifica una contraseña en claro contra su hash bcrypt."""
    return verify_password(password_plano, password_hash)


def hashear_password(password_plano: str) -> str:
    """Genera el hash bcrypt de una contraseña en claro."""
    return hash_password(password_plano)


def registrar_usuario(db: Session, email: str, password: str) -> Users:
    """Registra un usuario nuevo con email y contraseña.

    El resto de campos (razón social, documento, teléfono...) quedan a null
    y se completan más adelante desde la app.

    Lanza ValueError si el email ya está registrado.
    """
    if get_user_by_email(db, email):
        raise ValueError("El email ya está registrado")

    nuevo_usuario = Users(
        email=email,
        password_hash=hashear_password(password),
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def autenticar_usuario(
    db: Session,
    email: str,
    password: str
) -> Optional[Users]:
    """Autentica un usuario por email y contraseña.

    Retorna el usuario si las credenciales son correctas y está activo,
    None en cualquier otro caso.
    """
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verificar_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user


def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un JWT firmado con la SECRET_KEY y una expiración."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=_get_expire_minutes())
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _get_secret_key(), algorithm=ALGORITHM)


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Users:
    """Dependencia de FastAPI: valida el Bearer token y retorna el usuario.

    Lanza 401 si el token es inválido, ha expirado, el usuario no existe
    o está inactivo.
    """
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _get_secret_key(),
            algorithms=[ALGORITHM]
        )
        sub = payload.get("sub")
        if sub is None:
            raise credenciales_invalidas
        user_id = int(sub)
    except (PyJWTError, ValueError):
        raise credenciales_invalidas

    user = get_user_by_id(db, user_id)

    if not user or not user.is_active:
        raise credenciales_invalidas

    return user


# Alias para usar como dependencia al proteger rutas:
# usuario: Users = Depends(get_current_user)
get_current_user = obtener_usuario_actual
