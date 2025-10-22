"""
Celery Error Handling and Dead Letter Queue
Provides robust error handling, retry mechanisms, and dead letter queue functionality
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from celery import Task
from celery.exceptions import Retry, MaxRetriesExceededError
from celery.utils.log import get_task_logger
from app.config import settings
from app.tasks.notification_tasks import send_email, send_in_app_notification

logger = get_task_logger(__name__)


class DeadLetterQueue:
    """Dead Letter Queue for failed tasks"""
    
    def __init__(self):
        import redis
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.dlq_key = "celery:dead_letter_queue"
        
    def add_failed_task(self, task_id: str, task_name: str, args: tuple, kwargs: dict, 
                       error: str, retry_count: int, original_queue: str):
        """Add failed task to dead letter queue"""
        
        failed_task = {
            'task_id': task_id,
            'task_name': task_name,
            'args': args,
            'kwargs': kwargs,
            'error': str(error),
            'retry_count': retry_count,
            'original_queue': original_queue,
            'failed_at': datetime.utcnow().isoformat(),
            'retry_after': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store in Redis with TTL of 7 days
        self.redis_client.hset(
            self.dlq_key,
            task_id,
            json.dumps(failed_task)
        )
        self.redis_client.expire(self.dlq_key, 604800)  # 7 days
        
        logger.error(f"Task {task_name} ({task_id}) moved to dead letter queue")
        
    def get_failed_tasks(self, limit: int = 100) -> list:
        """Get failed tasks from dead letter queue"""
        
        tasks = self.redis_client.hgetall(self.dlq_key)
        failed_tasks = []
        
        for task_id, task_data in tasks.items():
            try:
                task_info = json.loads(task_data)
                failed_tasks.append(task_info)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse DLQ task data for {task_id}")
                
        return failed_tasks[:limit]
        
    def retry_failed_task(self, task_id: str) -> bool:
        """Retry a failed task from dead letter queue"""
        
        task_data = self.redis_client.hget(self.dlq_key, task_id)
        if not task_data:
            return False
            
        try:
            task_info = json.loads(task_data)
            
            # Import the task dynamically
            from app.celery_app import celery_app
            task = celery_app.tasks.get(task_info['task_name'])
            
            if not task:
                logger.error(f"Task {task_info['task_name']} not found")
                return False
                
            # Retry the task
            task.apply_async(
                args=task_info['args'],
                kwargs=task_info['kwargs'],
                queue=task_info['original_queue']
            )
            
            # Remove from DLQ
            self.redis_client.hdel(self.dlq_key, task_id)
            
            logger.info(f"Retried task {task_id} from dead letter queue")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry task {task_id}: {e}")
            return False
            
    def cleanup_old_tasks(self, days: int = 7):
        """Clean up old failed tasks"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        tasks = self.redis_client.hgetall(self.dlq_key)
        
        cleaned_count = 0
        for task_id, task_data in tasks.items():
            try:
                task_info = json.loads(task_data)
                failed_at = datetime.fromisoformat(task_info['failed_at'])
                
                if failed_at < cutoff_time:
                    self.redis_client.hdel(self.dlq_key, task_id)
                    cleaned_count += 1
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing DLQ task {task_id}: {e}")
                
        logger.info(f"Cleaned up {cleaned_count} old tasks from dead letter queue")


class RetryableTask(Task):
    """Base task class with enhanced retry and error handling"""
    
    # Retry configuration
    max_retries = 3
    default_retry_delay = 60
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    # Error handling
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    
    def __init__(self):
        super().__init__()
        self.dlq = DeadLetterQueue()
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        
        retry_count = self.request.retries
        retry_delay = self.get_retry_delay(retry_count)
        
        logger.warning(
            f"Task {self.name} ({task_id}) retry {retry_count}/{self.max_retries}: "
            f"{exc} - retrying in {retry_delay}s"
        )
        
        # Send retry notification for critical tasks
        if self.is_critical_task():
            self.send_retry_notification(task_id, exc, retry_count)
            
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails permanently"""
        
        retry_count = self.request.retries
        
        logger.error(
            f"Task {self.name} ({task_id}) failed permanently after "
            f"{retry_count} retries: {exc}"
        )
        
        # Add to dead letter queue
        self.dlq.add_failed_task(
            task_id=task_id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            retry_count=retry_count,
            original_queue=self.request.delivery_info.get('routing_key', 'default')
        )
        
        # Send failure notification
        self.send_failure_notification(task_id, exc, retry_count)
        
    def get_retry_delay(self, retry_count: int) -> int:
        """Calculate retry delay with exponential backoff and jitter"""
        
        if not self.retry_backoff:
            return self.default_retry_delay
            
        # Exponential backoff
        delay = min(
            self.default_retry_delay * (2 ** retry_count),
            self.retry_backoff_max
        )
        
        # Add jitter to prevent thundering herd
        if self.retry_jitter:
            import random
            jitter = random.uniform(0.5, 1.5)
            delay = int(delay * jitter)
            
        return delay
        
    def is_critical_task(self) -> bool:
        """Check if task is critical and requires special handling"""
        
        critical_tasks = [
            'app.tasks.notification_tasks.send_alert',
            'app.tasks.live_stream_tasks.check_alert_conditions',
            'app.tasks.maintenance_tasks.health_check'
        ]
        
        return self.name in critical_tasks
        
    def send_retry_notification(self, task_id: str, error: Exception, retry_count: int):
        """Send notification about task retry"""
        
        if not self.is_critical_task():
            return
            
        message = f"""
        Task Retry Alert
        
        Task: {self.name}
        Task ID: {task_id}
        Error: {error}
        Retry Count: {retry_count}/{self.max_retries}
        Time: {datetime.utcnow().isoformat()}
        
        This critical task is being retried. Please monitor for resolution.
        """
        
        # Send email notification
        send_email.delay(
            to=settings.FROM_EMAIL,
            subject=f"Task Retry Alert: {self.name}",
            body=message
        )
        
    def send_failure_notification(self, task_id: str, error: Exception, retry_count: int):
        """Send notification about task failure"""
        
        message = f"""
        Task Failure Alert
        
        Task: {self.name}
        Task ID: {task_id}
        Error: {error}
        Retry Count: {retry_count}/{self.max_retries}
        Time: {datetime.utcnow().isoformat()}
        
        This task has failed permanently and has been moved to the dead letter queue.
        Please investigate and retry manually if needed.
        """
        
        # Send email notification
        send_email.delay(
            to=settings.FROM_EMAIL,
            subject=f"Task Failure Alert: {self.name}",
            body=message
        )
        
        # Send in-app notification to admin users
        send_in_app_notification.delay(
            user_id="admin",  # TODO: Get admin user ID
            notification_data={
                "title": "Task Failure",
                "message": f"Task {self.name} has failed permanently",
                "type": "error",
                "task_id": task_id
            }
        )


class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
            
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        
        if self.last_failure_time is None:
            return True
            
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.recovery_timeout
        
    def _on_success(self):
        """Handle successful call"""
        
        self.failure_count = 0
        self.state = "CLOSED"
        
    def _on_failure(self):
        """Handle failed call"""
        
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


# Global instances
dlq = DeadLetterQueue()
circuit_breakers = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for service"""
    
    if service_name not in circuit_breakers:
        circuit_breakers[service_name] = CircuitBreaker()
        
    return circuit_breakers[service_name]


def setup_error_handling():
    """Set up comprehensive error handling"""
    
    # Set up periodic DLQ cleanup
    from app.celery_app import celery_app
    
    @celery_app.task
    def cleanup_dead_letter_queue():
        """Clean up old tasks from dead letter queue"""
        dlq.cleanup_old_tasks()
        
    # Schedule cleanup task to run daily
    celery_app.conf.beat_schedule['cleanup-dlq'] = {
        'task': 'app.celery_app.cleanup_dead_letter_queue',
        'schedule': 86400.0,  # Daily
    }
    
    logger.info("Error handling and dead letter queue configured")
