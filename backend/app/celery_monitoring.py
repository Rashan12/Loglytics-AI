"""
Celery Monitoring and Logging Configuration
Provides comprehensive monitoring, logging, and alerting for Celery tasks
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from celery import Task
from celery.events import EventReceiver
from celery.events.state import State
import redis
from app.config import settings
from app.tasks.notification_tasks import send_email, send_slack_notification


class CeleryMonitor:
    """Monitor Celery tasks and workers"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.state = State()
        self.logger = logging.getLogger(__name__)
        self.failed_tasks = []
        self.task_execution_times = {}
        
    def setup_logging(self):
        """Set up comprehensive logging for Celery tasks"""
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Set up task logger
        task_logger = logging.getLogger('celery.task')
        task_logger.setLevel(logging.INFO)
        
        # File handler for task logs
        task_file_handler = logging.FileHandler('logs/celery_tasks.log')
        task_file_handler.setFormatter(detailed_formatter)
        task_logger.addHandler(task_file_handler)
        
        # Set up worker logger
        worker_logger = logging.getLogger('celery.worker')
        worker_logger.setLevel(logging.INFO)
        
        # File handler for worker logs
        worker_file_handler = logging.FileHandler('logs/celery_workers.log')
        worker_file_handler.setFormatter(detailed_formatter)
        worker_logger.addHandler(worker_file_handler)
        
        # Set up beat logger
        beat_logger = logging.getLogger('celery.beat')
        beat_logger.setLevel(logging.INFO)
        
        # File handler for beat logs
        beat_file_handler = logging.FileHandler('logs/celery_beat.log')
        beat_file_handler.setFormatter(detailed_formatter)
        beat_logger.addHandler(beat_file_handler)
        
    def track_task_execution(self, task_id: str, task_name: str, start_time: float, end_time: float):
        """Track task execution time and performance metrics"""
        
        execution_time = end_time - start_time
        
        # Store execution time
        self.task_execution_times[task_id] = {
            'task_name': task_name,
            'execution_time': execution_time,
            'start_time': start_time,
            'end_time': end_time
        }
        
        # Log performance metrics
        self.logger.info(f"Task {task_name} ({task_id}) completed in {execution_time:.2f}s")
        
        # Store in Redis for monitoring
        self.redis_client.hset(
            f"task_metrics:{task_name}",
            task_id,
            execution_time
        )
        
        # Set expiry for metrics (24 hours)
        self.redis_client.expire(f"task_metrics:{task_name}", 86400)
        
    def track_task_failure(self, task_id: str, task_name: str, error: str, retry_count: int):
        """Track and alert on task failures"""
        
        failure_info = {
            'task_id': task_id,
            'task_name': task_name,
            'error': str(error),
            'retry_count': retry_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.failed_tasks.append(failure_info)
        
        # Log failure
        self.logger.error(f"Task {task_name} ({task_id}) failed: {error} (retry {retry_count})")
        
        # Store failure in Redis
        self.redis_client.lpush(
            "task_failures",
            f"{task_id}:{task_name}:{error}:{retry_count}:{datetime.utcnow().isoformat()}"
        )
        
        # Keep only last 100 failures
        self.redis_client.ltrim("task_failures", 0, 99)
        
        # Alert on critical failures
        if retry_count >= 3:  # Max retries reached
            self.send_failure_alert(failure_info)
            
    def send_failure_alert(self, failure_info: Dict):
        """Send alert for critical task failures"""
        
        alert_message = f"""
        Critical Task Failure Alert
        
        Task: {failure_info['task_name']}
        Task ID: {failure_info['task_id']}
        Error: {failure_info['error']}
        Retry Count: {failure_info['retry_count']}
        Timestamp: {failure_info['timestamp']}
        
        This task has reached maximum retry attempts and will not be retried.
        Please investigate immediately.
        """
        
        # Send email alert
        send_email.delay(
            to=settings.FROM_EMAIL,
            subject=f"Critical Task Failure: {failure_info['task_name']}",
            body=alert_message
        )
        
        # Send Slack alert if configured
        if settings.SLACK_WEBHOOK_URL:
            send_slack_notification.delay(
                webhook_url=settings.SLACK_WEBHOOK_URL,
                message=f"🚨 Critical task failure: {failure_info['task_name']} - {failure_info['error']}"
            )
        
        self.logger.critical(f"Sent failure alert for task {failure_info['task_name']}")
        
    def get_task_metrics(self, task_name: Optional[str] = None) -> Dict:
        """Get performance metrics for tasks"""
        
        if task_name:
            # Get metrics for specific task
            metrics = self.redis_client.hgetall(f"task_metrics:{task_name}")
            execution_times = [float(time) for time in metrics.values()]
            
            if execution_times:
                return {
                    'task_name': task_name,
                    'total_executions': len(execution_times),
                    'avg_execution_time': sum(execution_times) / len(execution_times),
                    'min_execution_time': min(execution_times),
                    'max_execution_time': max(execution_times)
                }
            return {'task_name': task_name, 'no_data': True}
        else:
            # Get metrics for all tasks
            all_metrics = {}
            for key in self.redis_client.scan_iter(match="task_metrics:*"):
                task_name = key.decode().split(":")[1]
                all_metrics[task_name] = self.get_task_metrics(task_name)
            return all_metrics
            
    def get_recent_failures(self, limit: int = 10) -> List[Dict]:
        """Get recent task failures"""
        
        failures = self.redis_client.lrange("task_failures", 0, limit - 1)
        parsed_failures = []
        
        for failure in failures:
            parts = failure.decode().split(":")
            if len(parts) >= 5:
                parsed_failures.append({
                    'task_id': parts[0],
                    'task_name': parts[1],
                    'error': parts[2],
                    'retry_count': int(parts[3]),
                    'timestamp': parts[4]
                })
        
        return parsed_failures
        
    def cleanup_old_metrics(self, days: int = 7):
        """Clean up old metrics data"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        cutoff_timestamp = cutoff_time.timestamp()
        
        # Clean up task execution times
        for task_id, metrics in list(self.task_execution_times.items()):
            if metrics['start_time'] < cutoff_timestamp:
                del self.task_execution_times[task_id]
        
        # Clean up Redis metrics
        for key in self.redis_client.scan_iter(match="task_metrics:*"):
            self.redis_client.delete(key)
            
        self.logger.info(f"Cleaned up metrics older than {days} days")


class TaskMonitoringMixin:
    """Mixin to add monitoring capabilities to Celery tasks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        end_time = time.time()
        start_time = getattr(self, '_start_time', end_time)
        
        # Track execution time
        monitor = CeleryMonitor()
        monitor.track_task_execution(
            task_id=task_id,
            task_name=self.name,
            start_time=start_time,
            end_time=end_time
        )
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        retry_count = getattr(self, 'request', {}).get('retries', 0)
        
        # Track failure
        monitor = CeleryMonitor()
        monitor.track_task_failure(
            task_id=task_id,
            task_name=self.name,
            error=str(exc),
            retry_count=retry_count
        )
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        retry_count = getattr(self, 'request', {}).get('retries', 0)
        
        monitor = CeleryMonitor()
        monitor.logger.warning(f"Task {self.name} ({task_id}) retry {retry_count}: {exc}")
        
    def __call__(self, *args, **kwargs):
        """Override to track start time"""
        self._start_time = time.time()
        return super().__call__(*args, **kwargs)


def setup_celery_monitoring():
    """Set up comprehensive Celery monitoring"""
    
    monitor = CeleryMonitor()
    monitor.setup_logging()
    
    # Set up periodic cleanup task
    from app.celery_app import celery_app
    
    @celery_app.task
    def cleanup_monitoring_data():
        """Clean up old monitoring data"""
        monitor.cleanup_old_metrics()
        
    # Schedule cleanup task to run daily
    celery_app.conf.beat_schedule['cleanup-monitoring-data'] = {
        'task': 'app.celery_app.cleanup_monitoring_data',
        'schedule': 86400.0,  # Daily
    }
    
    return monitor


# Global monitor instance
celery_monitor = setup_celery_monitoring()
