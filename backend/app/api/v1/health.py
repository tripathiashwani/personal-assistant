from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict:
    """Basic liveness check - does not touch the database."""
    return {"status": "ok"}


@router.get("/db")
async def health_check_db(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness check - confirms the app can talk to PostgreSQL."""
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
