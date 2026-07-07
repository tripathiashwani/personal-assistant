"""
Aggregates all v1 routers into a single APIRouter.

main.py only needs to import and include this one router. Future steps
add new routers (auth, documents, chats) here — main.py doesn't change.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.health import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(documents_router)
