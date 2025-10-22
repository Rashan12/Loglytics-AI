"""
Celery tasks for Loglytics AI
Background job processing for logs, analytics, notifications, and maintenance
"""

from app.tasks.log_processing_tasks import (
    process_log_file,
    generate_embeddings,
    cleanup_old_logs,
    compress_log_file,
)

from app.tasks.analytics_tasks import (
    calculate_analytics,
    update_project_analytics,
    generate_analytics_report,
    detect_anomalies,
    update_all_project_analytics,
    generate_weekly_reports,
)

from app.tasks.live_stream_tasks import (
    poll_cloud_logs,
    process_live_logs,
    check_alert_conditions,
    send_alerts,
    poll_all_connections,
    check_all_alert_conditions,
)

from app.tasks.notification_tasks import (
    send_email,
    send_slack_notification,
    create_jira_ticket,
    send_in_app_notification,
)

from app.tasks.maintenance_tasks import (
    cleanup_expired_api_keys,
    update_usage_statistics,
    backup_database,
    health_check,
)

__all__ = [
    # Log processing
    "process_log_file",
    "generate_embeddings",
    "cleanup_old_logs",
    "compress_log_file",

    # Analytics
    "calculate_analytics",
    "update_project_analytics",
    "generate_analytics_report",
    "detect_anomalies",
    "update_all_project_analytics",
    "generate_weekly_reports",

    # Live streaming
    "poll_cloud_logs",
    "process_live_logs",
    "check_alert_conditions",
    "send_alerts",
    "poll_all_connections",
    "check_all_alert_conditions",

    # Notifications
    "send_email",
    "send_slack_notification",
    "create_jira_ticket",
    "send_in_app_notification",

    # Maintenance
    "cleanup_expired_api_keys",
    "update_usage_statistics",
    "backup_database",
    "health_check",
]
