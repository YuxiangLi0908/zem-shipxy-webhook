from fastapi import APIRouter

from app.api import heartbeat, fleet_ship_eta

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"])
api_router.include_router(fleet_ship_eta.router, tags=["fleet_ship_eta"])
