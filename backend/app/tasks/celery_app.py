from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "prospect_analyzer",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=[
        "app.tasks.audit_tasks",
        "app.tasks.process_prospect",
        "app.tasks.process_batch",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minute hard limit for full audit
    task_soft_time_limit=540,
    worker_prefetch_multiplier=1,
)
