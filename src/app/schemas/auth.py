from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UpdateUserRequest(BaseModel):
    """Datos de empresa editables por el usuario autenticado.

    Todos los campos son opcionales: el frontend envía solo los que cambian.
    Email y password no se pueden actualizar por aquí.
    """
    razon_social: Optional[str] = Field(default=None, max_length=255)
    direccion_fiscal: Optional[str] = Field(default=None, max_length=255)
    documento: Optional[str] = Field(default=None, max_length=20)
    telefono: Optional[str] = Field(default=None, max_length=20)
    web: Optional[str] = Field(default=None, max_length=255)

    model_config = {"extra": "forbid"}


class UserResponse(BaseModel):
    """Datos del usuario autenticado. Nunca incluye password_hash.

    Los campos de empresa son opcionales: quedan a null tras el signup
    y se completan más adelante desde la app.
    """
    id: int
    email: EmailStr
    razon_social: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    documento: Optional[str] = None
    telefono: Optional[str] = None
    web: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}
