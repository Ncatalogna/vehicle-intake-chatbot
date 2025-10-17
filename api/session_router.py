from fastapi import APIRouter

# Crea un router principal
api_router = APIRouter(prefix='/api')

# Importa el router de locaciones
from routers import client_router, vehicle_router, eligibility_router

# Incluye los routers de cada recurso
api_router.include_router(client_router.router)
api_router.include_router(vehicle_router.router)
api_router.include_router(eligibility_router.router) 
