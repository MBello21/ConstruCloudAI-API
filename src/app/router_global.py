
from fastapi import APIRouter
from .routers.user import router as users_router
from .routers.presupuestos import router as presupuestos_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(presupuestos_router, prefix="/presupuestos", tags=["Presupuestos"])