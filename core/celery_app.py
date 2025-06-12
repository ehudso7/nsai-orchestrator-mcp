import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "nsai_orchestrator",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["core.tasks"]  # Include task modules
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    
    # Result backend settings
    result_expires=86400,  # Results expire after 1 day
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-old-executions": {
            "task": "core.tasks.cleanup_old_executions",
            "schedule": timedelta(hours=24),
            "options": {"expires": 3600}
        },
        "update-workflow-metrics": {
            "task": "core.tasks.update_workflow_metrics",
            "schedule": timedelta(hours=1),
            "options": {"expires": 300}
        },
        "check-api-key-expiration": {
            "task": "core.tasks.check_api_key_expiration",
            "schedule": timedelta(hours=12),
            "options": {"expires": 600}
        },
    },
    
    # Task routing
    task_routes={
        "core.tasks.execute_workflow_async": {"queue": "workflows"},
        "core.tasks.execute_agent_async": {"queue": "agents"},
        "core.tasks.analyze_data_async": {"queue": "analysis"},
        "core.tasks.scrape_web_async": {"queue": "scraping"},
    },
    
    # Error handling
    task_annotations={
        "*": {"rate_limit": "100/m"},  # Global rate limit
        "core.tasks.execute_agent_async": {
            "rate_limit": "30/m",
            "max_retries": 3,
            "default_retry_delay": 60,
        },
    }
)

# Task lifecycle hooks
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log task start"""
    logger.info(f"Task {task.name}[{task_id}] starting")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **extra):
    """Log task completion"""
    logger.info(f"Task {task.name}[{task_id}] completed with state: {state}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, 
                        kwargs=None, traceback=None, einfo=None, **extra):
    """Handle task failures"""
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")
    
    # You can add additional error handling here
    # e.g., send notifications, update database, etc.