from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints.health import health_check
from app.api.router import api_router
from app.core.config import settings
from app.core.rate_limit import setup_rate_limiting
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup & shutdown)."""
    logger.info(f"Starting up {settings.PROJECT_NAME} (Env: {settings.ENVIRONMENT})")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="B2B Sales Intelligence Platform — Website Auditing & Report Generation Engine",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Setup Rate Limiting
setup_rate_limiting(app, settings.redis_connection_url)

# CORS Configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler returning structured error JSON."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "path": request.url.path,
        },
    )


# Root Health Check (for orchestrators / load balancers)
@app.get("/health", tags=["Health"])
async def root_health():
    """Root level health probe alias."""
    from app.core.database import AsyncSessionLocal
    from datetime import datetime
    import redis.asyncio as aioredis
    from sqlalchemy import text

    db_status = "connected"
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"error: {str(e)}"

    redis_status = "connected"
    try:
        r = aioredis.from_url(settings.redis_connection_url, decode_responses=True, socket_timeout=3.0)
        await r.ping()
        await r.aclose()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    healthy = (db_status == "connected") and (redis_status == "connected")
    return {
        "status": "healthy" if healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {"database": db_status, "redis": redis_status},
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
    }


# Direct alias for POST /prospect/web-form (matching prompt architecture)
from app.api.endpoints.prospects import intake_web_form
app.add_api_route(
    "/prospect/web-form",
    intake_web_form,
    methods=["POST"],
    tags=["Prospects"],
    summary="Manual Prospect Intake Alias",
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["General"])
async def root_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }
