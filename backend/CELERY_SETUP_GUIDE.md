# Celery Task Queue Setup Guide

This guide provides comprehensive instructions for setting up and managing the Celery task queue system in Loglytics AI.

## Overview

The Celery task queue system handles background job processing for:
- Log file processing and analysis
- Analytics calculations and reporting
- Real-time log streaming and monitoring
- Notification delivery (email, Slack, Jira, in-app)
- System maintenance and cleanup tasks

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

## Quick Start

### 1. Start Redis (if not already running)

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or using Docker Compose
docker-compose -f docker-compose.celery.yml up redis -d
```

### 2. Start Celery Services

```bash
# Start all services (worker, beat, flower)
python scripts/start_celery.py

# Or start individual services
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
celery -A app.celery_app flower --port=5555
```

### 3. Test the Setup

```bash
# Run comprehensive tests
python scripts/test_celery.py

# Check worker status
python scripts/celery_manager.py workers
```

## Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:password@localhost/loglytics
REDIS_URL=redis://localhost:6379/0

# Optional (with defaults)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_MAX_RETRIES=3
CELERY_TASK_DEFAULT_RETRY_DELAY=60

# Notification services (optional)
SENDGRID_API_KEY=your_sendgrid_key
SLACK_WEBHOOK_URL=https://hooks.slack.com/your_webhook
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_token
```

### Task Queues

The system uses three priority queues:

- **high-priority**: Critical alerts, notifications
- **default**: Log processing, analytics, live streaming
- **low-priority**: Cleanup, maintenance tasks

### Periodic Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| Poll Live Log Connections | Every 30 seconds | Check for new logs from cloud providers |
| Check Alert Conditions | Every 5 minutes | Evaluate alert rules |
| Update Project Analytics | Every hour | Recalculate project metrics |
| Cleanup Old Logs | Daily at 2 AM | Remove logs older than 30 days |
| Cleanup Expired API Keys | Daily at 2:30 AM | Remove expired authentication keys |
| Update Usage Statistics | Daily at 3 AM | Calculate user usage metrics |
| Health Check | Every 15 minutes | Monitor system health |
| Generate Weekly Reports | Sundays at 8 AM | Create weekly analytics reports |
| Backup Database | Daily at 1 AM | Create database backups |

## Management Commands

### Start/Stop Services

```bash
# Start all Celery services
python scripts/start_celery.py

# Stop all Celery services
python scripts/stop_celery.py

# Start with Flower monitoring
START_FLOWER=true python scripts/start_celery.py
```

### Monitor Tasks

```bash
# List active tasks
python scripts/celery_manager.py active

# List scheduled tasks
python scripts/celery_manager.py scheduled

# List failed tasks
python scripts/celery_manager.py failed

# List dead letter queue
python scripts/celery_manager.py dlq

# Get task metrics
python scripts/celery_manager.py metrics
python scripts/celery_manager.py metrics --task-name "process_log_file"

# Get worker statistics
python scripts/celery_manager.py workers
```

### Troubleshooting

```bash
# Retry failed task
python scripts/celery_manager.py retry --task-id "task_id_here"

# Purge queue
python scripts/celery_manager.py purge --queue "default"

# Restart workers
python scripts/celery_manager.py restart
```

## Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.celery.yml up -d

# View logs
docker-compose -f docker-compose.celery.yml logs -f

# Scale workers
docker-compose -f docker-compose.celery.yml up -d --scale celery-worker=3
```

### Services

- **redis**: Redis broker and result backend
- **celery-worker**: Main worker processing all queues
- **celery-worker-high**: High-priority worker for critical tasks
- **celery-beat**: Periodic task scheduler
- **celery-flower**: Web-based monitoring interface

## Monitoring and Alerting

### Flower Web Interface

Access Flower at `http://localhost:5555` to monitor:
- Active tasks
- Task history
- Worker statistics
- Task execution times
- Error rates

### Log Files

- `logs/celery_tasks.log`: Task execution logs
- `logs/celery_workers.log`: Worker logs
- `logs/celery_beat.log`: Scheduler logs

### Health Checks

The system includes comprehensive health monitoring:
- Database connectivity
- Redis connectivity
- Worker status
- Disk space
- Memory usage
- Task failure rates

### Alerting

Automatic alerts are sent for:
- Critical task failures
- Worker offline events
- High error rates
- System health issues
- Dead letter queue items

## Error Handling

### Retry Mechanism

- **Max Retries**: 3 attempts
- **Retry Delay**: Exponential backoff (60s, 120s, 240s)
- **Jitter**: Random delay variation to prevent thundering herd
- **Max Delay**: 10 minutes

### Dead Letter Queue

Failed tasks are moved to a dead letter queue where they can be:
- Manually retried
- Inspected for debugging
- Automatically cleaned up after 7 days

### Circuit Breaker

External service calls are protected by circuit breakers that:
- Open after 5 consecutive failures
- Automatically reset after 60 seconds
- Prevent cascading failures

## Performance Tuning

### Worker Configuration

```python
# High concurrency for CPU-bound tasks
CELERY_WORKER_CONCURRENCY=8

# Prefetch multiplier for I/O-bound tasks
CELERY_WORKER_PREFETCH_MULTIPLIER=1

# Max tasks per child to prevent memory leaks
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
```

### Queue Routing

```python
# Route critical tasks to high-priority queue
task_routes = {
    "app.tasks.notification_tasks.send_alert": {"queue": "high-priority"},
    "app.tasks.live_stream_tasks.check_alert_conditions": {"queue": "high-priority"},
}
```

### Memory Management

- Workers are restarted after processing 1000 tasks
- Old metrics are cleaned up daily
- Failed tasks are purged after 7 days
- Log files are rotated automatically

## Troubleshooting

### Common Issues

1. **Workers not starting**
   - Check Redis connectivity
   - Verify environment variables
   - Check worker logs

2. **Tasks not executing**
   - Verify task registration
   - Check queue routing
   - Monitor worker status

3. **High memory usage**
   - Reduce worker concurrency
   - Lower prefetch multiplier
   - Enable task result expiry

4. **Task failures**
   - Check dead letter queue
   - Review error logs
   - Verify task dependencies

### Debug Commands

```bash
# Check Celery status
celery -A app.celery_app inspect stats

# Check registered tasks
celery -A app.celery_app inspect registered

# Check active tasks
celery -A app.celery_app inspect active

# Check scheduled tasks
celery -A app.celery_app inspect scheduled
```

### Log Analysis

```bash
# Monitor task execution
tail -f logs/celery_tasks.log

# Check for errors
grep "ERROR" logs/celery_tasks.log

# Monitor worker health
tail -f logs/celery_workers.log
```

## Security Considerations

- API keys are stored in environment variables
- Database connections use connection pooling
- Task results are stored with TTL
- Sensitive data is not logged
- Workers run with limited privileges

## Backup and Recovery

- Database backups are created daily
- Task state is persisted in Redis
- Configuration is version controlled
- Logs are rotated and archived

## Scaling

### Horizontal Scaling

```bash
# Add more workers
docker-compose -f docker-compose.celery.yml up -d --scale celery-worker=5

# Add more high-priority workers
docker-compose -f docker-compose.celery.yml up -d --scale celery-worker-high=3
```

### Vertical Scaling

- Increase worker concurrency
- Add more memory to workers
- Use faster storage for Redis
- Optimize database queries

## Support

For issues and questions:
1. Check the logs
2. Run the test suite
3. Review this documentation
4. Check the GitHub issues
5. Contact the development team
