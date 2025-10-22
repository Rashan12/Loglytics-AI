"""
Celery application configuration for Loglytics AI
Handles background task processing with Redis as broker
"""

from celery import Celery
from celery.schedules import crontab
from app.config import settings
from app.celery_monitoring import TaskMonitoringMixin
from app.celery_error_handling import RetryableTask, setup_error_handling
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "loglytics_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.log_processing_tasks",
        "app.tasks.analytics_tasks",
        "app.tasks.live_stream_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.maintenance_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,

    # Timezone
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,

    # Task execution
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,

    # Worker configuration
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,

    # Result backend
    result_expires=settings.CELERY_RESULT_EXPIRES,
    result_persistent=True,

    # Task routing
    task_routes={
        # High priority tasks (alerts, critical operations)
        "app.tasks.notification_tasks.send_alert": {"queue": settings.CELERY_HIGH_PRIORITY_QUEUE},
        "app.tasks.live_stream_tasks.check_alert_conditions": {"queue": settings.CELERY_HIGH_PRIORITY_QUEUE},

        # Normal priority tasks (processing, analytics)
        "app.tasks.log_processing_tasks.*": {"queue": settings.CELERY_DEFAULT_QUEUE},
        "app.tasks.analytics_tasks.*": {"queue": settings.CELERY_DEFAULT_QUEUE},
        "app.tasks.live_stream_tasks.process_live_logs": {"queue": settings.CELERY_DEFAULT_QUEUE},

        # Low priority tasks (cleanup, maintenance)
        "app.tasks.maintenance_tasks.*": {"queue": settings.CELERY_LOW_PRIORITY_QUEUE},
    },

    # Task default retry configuration
    task_default_retry_delay=settings.CELERY_TASK_DEFAULT_RETRY_DELAY,
    task_max_retries=settings.CELERY_TASK_MAX_RETRIES,

    # Beat schedule for periodic tasks
    beat_schedule={
        # Poll live log connections every 30 seconds
        "poll-live-log-connections": {
            "task": "app.tasks.live_stream_tasks.poll_all_connections",
            "schedule": 30.0,  # Run every 30 seconds
        },

        # Check alert conditions every 5 minutes
        "check-alert-conditions": {
            "task": "app.tasks.live_stream_tasks.check_all_alert_conditions",
            "schedule": 300.0,  # Run every 5 minutes
        },

        # Update project analytics every hour
        "update-project-analytics": {
            "task": "app.tasks.analytics_tasks.update_all_project_analytics",
            "schedule": 3600.0,  # Run every hour
        },

        # Cleanup old logs daily at 2 AM
        "cleanup-old-logs": {
            "task": "app.tasks.maintenance_tasks.cleanup_old_logs",
            "schedule": crontab(hour=2, minute=0),
            "kwargs": {"days": 30},
        },

        # Cleanup expired API keys daily at 2:30 AM
        "cleanup-expired-api-keys": {
            "task": "app.tasks.maintenance_tasks.cleanup_expired_api_keys",
            "schedule": crontab(hour=2, minute=30),
        },

        # Update usage statistics daily at 3 AM
        "update-usage-statistics": {
            "task": "app.tasks.maintenance_tasks.update_usage_statistics",
            "schedule": crontab(hour=3, minute=0),
        },

        # System health check every 15 minutes
        "health-check": {
            "task": "app.tasks.maintenance_tasks.health_check",
            "schedule": 900.0,  # Run every 15 minutes
        },

        # Generate weekly reports on Sundays at 8 AM
        "generate-weekly-reports": {
            "task": "app.tasks.analytics_tasks.generate_weekly_reports",
            "schedule": crontab(day_of_week=0, hour=8, minute=0),
        },

        # Backup database daily at 1 AM
        "backup-database": {
            "task": "app.tasks.maintenance_tasks.backup_database",
            "schedule": crontab(hour=1, minute=0),
        },
    },
)

# Task retry configuration with exponential backoff
celery_app.conf.task_annotations = {
    "*": {
        "max_retries": 3,
        "retry_backoff": True,
        "retry_backoff_max": 600,  # Maximum 10 minutes
        "retry_jitter": True,  # Add randomness to prevent thundering herd
    }
}

# Set up error handling
setup_error_handling()

# Configure task base classes
celery_app.Task = RetryableTask

# Set up monitoring
from app.celery_monitoring import setup_celery_monitoring
celery_monitor = setup_celery_monitoring()

logger.info(f"Celery app initialized with broker: {settings.CELERY_BROKER_URL}")
