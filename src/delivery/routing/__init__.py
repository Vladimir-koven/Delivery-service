from fastapi import APIRouter

from delivery.routing import couriers, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(couriers.router)
