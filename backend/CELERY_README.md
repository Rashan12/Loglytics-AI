# Celery Task Queue Setup - Loglytics AI

## Overview

Loglytics AI uses Celery for background task processing with Redis as the message broker. This enables asynchronous processing of log files, analytics calculations, notifications, and maintenance tasks.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│    Redis    │◀────│   Celery    │
│   Backend   │     │   (Broker)  │     │   Worker    │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │   Celery    │
                    │    Beat     │
                    │ (Scheduler) │
                    └─────────────┘
```

## Task Queues

The system uses three priority queues:

- **high-priority**: Alerts, critical notifications
- **default**: Log processing, analytics
- **low-priority**: Cleanup, maintenance tasks

## Task Categories

### 1. Log Processing Tasks (`log_processing_tasks.py`)

- **process_log_file**: Parse and store logs from uploaded files
- **generate_embeddings**: Create RAG vectors for semantic search
- **cleanup_old_logs**: Delete logs older than X days
- **compress_log_file**: Compress old log files
- **parse_structured_logs**: Parse JSON, CSV formats
- **extract_log_metadata**: Extract metadata from logs

### 2. Analytics Tasks (`analytics_tasks.py`)

- **calculate_analytics**: Run analytics on log file
- **update_project_analytics**: Aggregate project-level stats
- **generate_analytics_report**: Create and email reports
- **detect_anomalies**: ML-based anomaly detection
- **update_all_project_analytics**: Periodic analytics update
- **generate_weekly_reports**: Weekly report generation
- **calculate_log_patterns**: Identify recurring patterns
- **generate_insights**: AI-powered insights

### 3. Live Stream Tasks (`live_stream_tasks.py`)

- **poll_cloud_logs**: Fetch logs from cloud providers
- **process_live_logs**: Process real-time log batches
- **check_alert_conditions**: Evaluate alert rules
- **send_alerts**: Dispatch alerts via channels
- **poll_all_connections**: Periodic cloud polling
- **check_all_alert_conditions**: Periodic alert checking
- **update_live_analytics**: Real-time analytics

### 4. Notification Tasks (`notification_tasks.py`)

- **send_email**: SendGrid email delivery
- **send_slack_notification**: Slack webhook notifications
- **create_jira_ticket**: Jira issue creation
- **send_in_app_notification**: In-app notifications
- **send_webhook**: Generic webhook delivery
- **send_sms**: SMS notifications
- **send_push_notification**: Mobile push notifications

### 5. Maintenance Tasks (`maintenance_tasks.py`)

- **cleanup_expired_api_keys**: Remove expired keys
- **update_usage_statistics**: Calculate daily usage
- **backup_database**: Automated DB backups
- **health_check**: System health monitoring
- **cleanup_temp_files**: Remove old temp files
- **optimize_database**: Database optimization
- **generate_system_report**: System metrics report
- **cleanup_old_notifications**: Remove old notifications

## Periodic Tasks (Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| poll_all_connections | Every 30s | Poll active live log connections |
| check_all_alert_conditions | Every 5min | Check alert conditions |
| update_all_project_analytics | Every hour | Update project analytics |
| cleanup_old_logs | Daily 2 AM | Clean up old logs (30 days) |
| cleanup_expired_api_keys | Daily 2:30 AM | Remove expired API keys |
| update_usage_statistics | Daily 3 AM | Update usage stats |
| health_check | Every 15min | System health check |
| generate_weekly_reports | Sunday 8 AM | Generate weekly reports |
| backup_database | Daily 1 AM | Database backup |

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Add to `.env`:

```env
# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Notifications
SENDGRID_API_KEY=your_sendgrid_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_email
JIRA_API_TOKEN=your_jira_api_token
```

## Running Celery

### Using Docker Compose (Recommended)

```bash
# Start all services including Celery
docker-compose up -d

# View Celery worker logs
docker-compose logs -f celery-worker

# View Celery beat logs
docker-compose logs -f celery-beat

# Access Flower monitoring at http://localhost:5555
```

### Manual Execution (Linux/Mac)

```bash
cd backend

# Start worker
./scripts/start_celery_worker.sh

# Start beat (in separate terminal)
./scripts/start_celery_beat.sh

# Start Flower monitoring (in separate terminal)
./scripts/start_flower.sh

# Check status
./scripts/celery_status.sh

# Stop all
./scripts/stop_celery.sh
```

### Manual Execution (Windows)

```bash
cd backend

# Start worker
scripts\start_celery_worker.bat

# Start beat (in separate terminal)
scripts\start_celery_beat.bat

# Start Flower (in separate terminal)
scripts\start_flower.bat
```

## Monitoring with Flower

Flower provides a web-based monitoring UI for Celery.

- **URL**: http://localhost:5555
- **Features**:
  - Real-time task monitoring
  - Worker status and stats
  - Task history and results
  - Rate limiting controls
  - Task revocation

## Task Usage Examples

### From Python Code

```python
from app.tasks import (
    process_log_file,
    generate_analytics_report,
    send_email
)

# Queue a task
task = process_log_file.delay(log_file_id="123")

# Get task result
result = task.get(timeout=10)

# Chain tasks
from celery import chain
workflow = chain(
    process_log_file.s(log_file_id="123"),
    generate_embeddings.s(),
    calculate_analytics.s()
)
workflow.apply_async()

# Group tasks (parallel execution)
from celery import group
job = group(
    process_log_file.s(id) for id in log_file_ids
)
result = job.apply_async()
```

### From FastAPI Endpoint

```python
from fastapi import APIRouter
from app.tasks import process_log_file

router = APIRouter()

@router.post("/logs/process/{log_file_id}")
async def process_log(log_file_id: str):
    # Queue background task
    task = process_log_file.delay(log_file_id)

    return {
        "task_id": task.id,
        "status": "queued"
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

## Configuration

### Worker Configuration

```python
# app/config.py
CELERY_WORKER_CONCURRENCY: int = 4  # Number of worker processes
CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 1000  # Prevent memory leaks
CELERY_WORKER_PREFETCH_MULTIPLIER: int = 4  # Tasks to prefetch
```

### Task Retry Configuration

```python
# Default retry settings
CELERY_TASK_MAX_RETRIES: int = 3
CELERY_TASK_DEFAULT_RETRY_DELAY: int = 60  # seconds

# Per-task configuration
@celery_app.task(
    max_retries=5,
    default_retry_delay=30,
    autoretry_for=(ConnectionError,)
)
def my_task():
    pass
```

### Queue Routing

Tasks are automatically routed to appropriate queues based on priority:

```python
# High priority (alerts)
send_alerts -> high-priority queue

# Normal priority (processing)
process_log_file -> default queue

# Low priority (cleanup)
cleanup_old_logs -> low-priority queue
```

## Troubleshooting

### Worker Not Processing Tasks

```bash
# Check worker is running
celery -A app.celery_app inspect active

# Check Redis connection
redis-cli ping

# Check worker logs
docker-compose logs celery-worker
```

### Tasks Stuck in Queue

```bash
# Purge all tasks
celery -A app.celery_app purge

# Revoke specific task
celery -A app.celery_app revoke <task_id>

# Restart workers
docker-compose restart celery-worker
```

### Memory Issues

```bash
# Monitor worker memory
celery -A app.celery_app inspect stats

# Reduce concurrency
docker-compose stop celery-worker
# Edit docker-compose.yml: --concurrency=2
docker-compose up -d celery-worker
```

## Best Practices

1. **Task Design**:
   - Keep tasks idempotent
   - Handle failures gracefully
   - Use task retries with exponential backoff
   - Log task execution details

2. **Performance**:
   - Use task groups for parallel execution
   - Set appropriate time limits
   - Monitor task execution times
   - Use result expiry to save space

3. **Monitoring**:
   - Use Flower for real-time monitoring
   - Set up alerts for task failures
   - Track queue lengths
   - Monitor worker health

4. **Scaling**:
   - Add more workers for high load
   - Use separate workers per queue
   - Scale Redis if needed
   - Consider task prioritization

## Security

- Secure Redis with password
- Use TLS for Redis in production
- Validate task inputs
- Sanitize user data before processing
- Implement rate limiting
- Monitor for suspicious task patterns

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
