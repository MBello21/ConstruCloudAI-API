from .auth import LoginRequest, SignupRequest, TokenResponse
from .user import UserCreate, UserResponse
from .clientes import ClienteCreate, ClienteResponse, ClienteUpdate
from .presupuestos import PresupuestoCompletoResponse, PresupuestoCreadoResponse
from .presupuestos_ia import (
    SolicitudIAPresupuesto,
    DetalleEstructura,
    CapituloEstructura,
    EstructuraPresupuesto,
    ReferenciaRAG,
    PresupuestoGeneradoResponse,
)
from .capitulos import CapituloCreate, CapituloResponse, CapituloUpdate
from .detalles import DetalleCreate, DetalleResponse, DetalleUpdate
