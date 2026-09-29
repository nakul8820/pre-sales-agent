from datetime import datetime
from fastapi import APIRouter, Depends, status
import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_db
from app.schemas.health import HealthResponse, ServiceStatus
from app.utils.logger import logger

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Readiness Check",
    description="Validates overall service operational readiness including PostgreSQL and Redis connections.",
)
async def health_check(db: AsyncSession = Depends(get_async_db)) -> HealthResponse:
    # 1. Database Check
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"error: {str(e)}"

    # 2. Redis Check
    redis_status = "connected"
    try:
        r = aioredis.from_url(
            settings.redis_connection_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=3.0,
        )
        ping_res = await r.ping()
        await r.aclose()
        if not ping_res:
            redis_status = "error: ping failed"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = f"error: {str(e)}"

    overall_healthy = (db_status == "connected") and (redis_status == "connected")

    return HealthResponse(
        status="healthy" if overall_healthy else "degraded",
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        services=ServiceStatus(
            database=db_status,
            redis=redis_status,
        ),
    )
