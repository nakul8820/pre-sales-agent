import asyncio
import uuid
from typing import Dict, Any
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.batch_job import BatchJob, BatchStatus
from app.models.prospect import Prospect
from app.tasks.celery_app import celery_app
from app.tasks.process_prospect import process_prospect_task
from app.utils.logger import logger


async def _fanout_batch_async(batch_job_id_str: str) -> Dict[str, Any]:
    batch_job_id = uuid.UUID(batch_job_id_str)
    
    async with AsyncSessionLocal() as db:
        stmt = select(BatchJob).where(BatchJob.id == batch_job_id)
        result = await db.execute(stmt)
        batch = result.scalar_one_or_none()
        
        if not batch:
            logger.error(f"BatchJob {batch_job_id} not found.")
            return {"error": "BatchJob not found."}
            
        logger.info(f"Fanning out batch {batch_job_id}")
        
        # Mark as running
        batch.status = BatchStatus.RUNNING
        batch.started_at = datetime.now(timezone.utc)
        
        # Fetch associated prospects
        prospect_stmt = select(Prospect).where(Prospect.batch_id == batch_job_id)
        p_result = await db.execute(prospect_stmt)
        prospects = p_result.scalars().all()
        
        batch.total_count = len(prospects)
        await db.commit()
        
        # Dispatch tasks
        for p in prospects:
            process_prospect_task.delay(str(p.id))
            
        logger.info(f"Dispatched {len(prospects)} prospect tasks for batch {batch_job_id}")
        
        return {
            "batch_job_id": str(batch_job_id),
            "status": "fanned_out",
            "total_dispatched": len(prospects)
        }


@celery_app.task(bind=True, name="app.tasks.process_batch.process_batch_task")
def process_batch_task(self, batch_job_id: str) -> Dict[str, Any]:
    """Fans out process_prospect_task for each prospect in a BatchJob."""
    logger.info(f"Task {self.request.id}: Starting process_batch_task for {batch_job_id}")
    
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    result = loop.run_until_complete(_fanout_batch_async(batch_job_id))
    return result
