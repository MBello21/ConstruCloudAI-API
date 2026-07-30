
from fastapi import APIRouter
from .routers.user import router as users_router
from .routers.presupuestos import router as presupuestos_router
from .routers.clientes import router as clientes_router
from .routers.capitulos import router as capitulos_router
from .routers.detalles import router as detalles_router


api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(
    presupuestos_router, prefix="/presupuestos", tags=["Presupuestos"])
api_router.include_router(
    clientes_router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(
    capitulos_router, prefix="/capitulos", tags=["Capitulos"])
api_router.include_router(
    detalles_router, prefix="/detalles", tags=["Detalles"])
