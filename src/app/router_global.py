
from fastapi import APIRouter
from .routers.user import router as users_router
from .routers.presupuestos import router as presupuestos_router
<<<<<<< HEAD
=======
from .routers.clientes import router as clientes_router
>>>>>>> 482b90c2a11552e1eac1cc13373dcabe016d702e

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(presupuestos_router, prefix="/presupuestos", tags=["Presupuestos"])
<<<<<<< HEAD
=======
api_router.include_router(clientes_router, prefix="/clientes", tags=["Clientes"])
>>>>>>> 482b90c2a11552e1eac1cc13373dcabe016d702e
