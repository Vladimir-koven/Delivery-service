from fastapi import APIRouter

from delivery.routing import auth, couriers, health, orders

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(couriers.router)
api_router.include_router(orders.router)
