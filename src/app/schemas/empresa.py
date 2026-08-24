from pydantic import BaseModel, EmailStr, Field


class EmpresaUpdate(BaseModel):
    razon_social: str | None = Field(default=None, max_length=255)
    direccion_fiscal: str | None = Field(default=None, max_length=255)
    documento: str | None = Field(default=None, max_length=20)
    telefono: str | None = Field(default=None, max_length=20)
    web: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    model_config = {"extra": "forbid"}


class EmpresaResponse(BaseModel):
    id: int
    razon_social: str | None = None
    direccion_fiscal: str | None = None
    documento: str | None = None
    telefono: str | None = None
    web: str | None = None
    email: str | None = None
    model_config = {"from_attributes": True}
