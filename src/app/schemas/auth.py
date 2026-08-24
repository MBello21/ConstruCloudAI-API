from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nombre_completo: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UpdateUserRequest(BaseModel):
    nombre_completo: str | None = Field(default=None, max_length=255)
    cargo: str | None = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=20)
    model_config = {"extra": "forbid"}


class CreateUserEmpresaRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nombre_completo: str | None = None
    rol: str = Field(default="usuario", pattern="^(admin|gestor|usuario)$")


class UpdateUserRolRequest(BaseModel):
    rol: str = Field(pattern="^(admin|gestor|usuario)$")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nombre_completo: str | None = None
    cargo: str | None = None
    rol: str | None = None
    telefono: str | None = None
    empresa_id: int | None = None
    is_active: bool
    model_config = {"from_attributes": True}
