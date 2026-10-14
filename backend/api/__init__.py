from fastapi import APIRouter
from backend.api import health, captions, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(captions.router, prefix="/api", tags=["captions"])
api_router.include_router(ui.router, tags=["ui"])
