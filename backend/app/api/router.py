from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.prospects import router as prospects_router
from app.api.endpoints.audits import router as audits_router
from app.api.endpoints.reports import router as reports_router
from app.api.endpoints.batch import router as batch_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="", tags=["Health"])
api_router.include_router(prospects_router, prefix="/prospects", tags=["Prospects"])
api_router.include_router(audits_router, prefix="/audits", tags=["Audits"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(batch_router, prefix="/batch", tags=["Batch"])
