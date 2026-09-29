from app.api.endpoints.health import router as health_router
from app.api.endpoints.prospects import router as prospects_router
from app.api.endpoints.audits import router as audits_router
from app.api.endpoints.reports import router as reports_router
from app.api.endpoints.batch import router as batch_router

__all__ = [
    "health_router",
    "prospects_router",
    "audits_router",
    "reports_router",
    "batch_router",
]
