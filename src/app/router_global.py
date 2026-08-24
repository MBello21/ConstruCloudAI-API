
from fastapi import APIRouter, Depends
from .routers.auth import router as auth_router
from .routers.user import router as users_router
from .routers.presupuestos import router as presupuestos_router
from .routers.clientes import router as clientes_router
from .routers.capitulos import router as capitulos_router
from .routers.detalles import router as detalles_router
from .routers.empresa import router as empresa_router
from .services.auth_service import get_current_user


api_router = APIRouter()

# Dependencia de protección JWT: se aplica a todos los routers menos auth.
protegido = [Depends(get_current_user)]


api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(
    users_router, prefix="/users", tags=["Users"],
    dependencies=protegido)
api_router.include_router(
    presupuestos_router, prefix="/presupuestos", tags=["Presupuestos"],
    dependencies=protegido)
api_router.include_router(
    clientes_router, prefix="/clientes", tags=["Clientes"],
    dependencies=protegido)
api_router.include_router(
    capitulos_router, prefix="/capitulos", tags=["Capitulos"],
    dependencies=protegido)
api_router.include_router(
    detalles_router, prefix="/detalles", tags=["Detalles"],
    dependencies=protegido)
api_router.include_router(
    empresa_router, prefix="/empresa", tags=["Empresa"],
    dependencies=protegido)
