import time
from app.tasks.celery_app import celery_app
from app.utils.logger import logger


@celery_app.task(name="app.tasks.audit_tasks.run_prospect_audit", bind=True)
def run_prospect_audit(self, prospect_id: str):
    """Background task skeleton for running website audit on a prospect."""
    logger.info(f"Starting audit task {self.request.id} for prospect {prospect_id}")
    time.sleep(1)
    logger.info(f"Completed audit task {self.request.id} for prospect {prospect_id}")
    return {"prospect_id": prospect_id, "status": "completed"}
