import asyncio
import uuid
from typing import Dict, Any

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.prospect import Prospect, ProspectStatus
from app.services.orchestrator import analyzer_orchestrator
from app.tasks.celery_app import celery_app
from app.utils.logger import logger


async def _run_prospect_audit_async(prospect_id_str: str) -> Dict[str, Any]:
    prospect_id = uuid.UUID(prospect_id_str)
    
    async with AsyncSessionLocal() as db:
        stmt = select(Prospect).where(Prospect.id == prospect_id)
        result = await db.execute(stmt)
        prospect = result.scalar_one_or_none()
        
        if not prospect:
            logger.error(f"Prospect {prospect_id} not found for async audit.")
            return {"error": f"Prospect {prospect_id} not found."}
            
        logger.info(f"Celery executing async audit for prospect {prospect_id}")
        
        try:
            audit_results = await analyzer_orchestrator.analyze_prospect(prospect, db)
            return {
                "prospect_id": str(prospect_id),
                "status": "success",
                "overall_score": audit_results.get("overall_score")
            }
        except Exception as e:
            logger.error(f"Error during async audit for prospect {prospect_id}: {e}")
            prospect.status = ProspectStatus.FAILED
            await db.commit()
            return {"error": str(e)}


@celery_app.task(bind=True, name="app.tasks.process_prospect.process_prospect_task", max_retries=3)
def process_prospect_task(self, prospect_id: str) -> Dict[str, Any]:
    """Runs full orchestrator audit on a single prospect from DB via Celery."""
    logger.info(f"Task {self.request.id}: Starting process_prospect_task for {prospect_id}")
    
    # Run the async orchestrator inside a new event loop for this Celery worker thread
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    result = loop.run_until_complete(_run_prospect_audit_async(prospect_id))
    return result
