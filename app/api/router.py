from fastapi import APIRouter

from app.api import heartbeat, ship_added

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"])
api_router.include_router(ship_added.router, tags=["ship_added"])
