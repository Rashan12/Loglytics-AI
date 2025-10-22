#!/usr/bin/env python3
"""
Celery Management Script
Provides commands to manage, monitor, and troubleshoot Celery tasks
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.celery_app import celery_app
from app.celery_monitoring import celery_monitor
from app.celery_error_handling import dlq


def list_active_tasks():
    """List currently active tasks"""
    print("Active Tasks:")
    print("-" * 50)
    
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    
    if not active_tasks:
        print("No active tasks found")
        return
        
    for worker, tasks in active_tasks.items():
        print(f"\nWorker: {worker}")
        for task in tasks:
            print(f"  - {task['name']} ({task['id']})")
            print(f"    Args: {task.get('args', [])}")
            print(f"    Started: {datetime.fromtimestamp(task['time_start'])}")


def list_scheduled_tasks():
    """List scheduled tasks"""
    print("Scheduled Tasks:")
    print("-" * 50)
    
    inspect = celery_app.control.inspect()
    scheduled_tasks = inspect.scheduled()
    
    if not scheduled_tasks:
        print("No scheduled tasks found")
        return
        
    for worker, tasks in scheduled_tasks.items():
        print(f"\nWorker: {worker}")
        for task in tasks:
            print(f"  - {task['name']} ({task['id']})")
            print(f"    ETA: {datetime.fromtimestamp(task['eta'])}")


def list_failed_tasks():
    """List recent failed tasks"""
    print("Recent Failed Tasks:")
    print("-" * 50)
    
    failures = celery_monitor.get_recent_failures(limit=20)
    
    if not failures:
        print("No recent failures found")
        return
        
    for failure in failures:
        print(f"\nTask: {failure['task_name']}")
        print(f"ID: {failure['task_id']}")
        print(f"Error: {failure['error']}")
        print(f"Retry Count: {failure['retry_count']}")
        print(f"Timestamp: {failure['timestamp']}")


def list_dead_letter_queue():
    """List tasks in dead letter queue"""
    print("Dead Letter Queue:")
    print("-" * 50)
    
    failed_tasks = dlq.get_failed_tasks(limit=20)
    
    if not failed_tasks:
        print("No tasks in dead letter queue")
        return
        
    for task in failed_tasks:
        print(f"\nTask: {task['task_name']}")
        print(f"ID: {task['task_id']}")
        print(f"Error: {task['error']}")
        print(f"Retry Count: {task['retry_count']}")
        print(f"Failed At: {task['failed_at']}")
        print(f"Original Queue: {task['original_queue']}")


def retry_failed_task(task_id: str):
    """Retry a failed task from dead letter queue"""
    print(f"Retrying task: {task_id}")
    
    success = dlq.retry_failed_task(task_id)
    
    if success:
        print(f"Task {task_id} has been queued for retry")
    else:
        print(f"Failed to retry task {task_id}")


def get_task_metrics(task_name: str = None):
    """Get performance metrics for tasks"""
    print("Task Performance Metrics:")
    print("-" * 50)
    
    metrics = celery_monitor.get_task_metrics(task_name)
    
    if isinstance(metrics, dict) and 'no_data' in metrics:
        print(f"No data available for task: {task_name}")
        return
        
    if task_name:
        # Single task metrics
        print(f"Task: {metrics['task_name']}")
        print(f"Total Executions: {metrics['total_executions']}")
        print(f"Average Execution Time: {metrics['avg_execution_time']:.2f}s")
        print(f"Min Execution Time: {metrics['min_execution_time']:.2f}s")
        print(f"Max Execution Time: {metrics['max_execution_time']:.2f}s")
    else:
        # All tasks metrics
        for task_name, task_metrics in metrics.items():
            if 'no_data' not in task_metrics:
                print(f"\nTask: {task_name}")
                print(f"  Total Executions: {task_metrics['total_executions']}")
                print(f"  Average Execution Time: {task_metrics['avg_execution_time']:.2f}s")
                print(f"  Min Execution Time: {task_metrics['min_execution_time']:.2f}s")
                print(f"  Max Execution Time: {task_metrics['max_execution_time']:.2f}s")


def get_worker_stats():
    """Get worker statistics"""
    print("Worker Statistics:")
    print("-" * 50)
    
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    
    if not stats:
        print("No workers found")
        return
        
    for worker, worker_stats in stats.items():
        print(f"\nWorker: {worker}")
        print(f"  Status: {worker_stats.get('status', 'Unknown')}")
        print(f"  Pool: {worker_stats.get('pool', {}).get('implementation', 'Unknown')}")
        print(f"  Processes: {worker_stats.get('pool', {}).get('processes', 'Unknown')}")
        print(f"  Max Concurrency: {worker_stats.get('pool', {}).get('max-concurrency', 'Unknown')}")
        print(f"  Active Tasks: {worker_stats.get('total', {}).get('active', 0)}")
        print(f"  Processed Tasks: {worker_stats.get('total', {}).get('task-received', 0)}")


def purge_queue(queue_name: str):
    """Purge all tasks from a queue"""
    print(f"Purging queue: {queue_name}")
    
    try:
        celery_app.control.purge()
        print(f"Queue {queue_name} purged successfully")
    except Exception as e:
        print(f"Error purging queue: {e}")


def restart_workers():
    """Restart all workers"""
    print("Restarting workers...")
    
    try:
        celery_app.control.broadcast('shutdown')
        print("Workers restart command sent")
    except Exception as e:
        print(f"Error restarting workers: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Celery Management Script")
    parser.add_argument("command", choices=[
        "active", "scheduled", "failed", "dlq", "retry", "metrics", 
        "workers", "purge", "restart"
    ], help="Command to execute")
    parser.add_argument("--task-id", help="Task ID for retry command")
    parser.add_argument("--task-name", help="Task name for metrics command")
    parser.add_argument("--queue", help="Queue name for purge command")
    
    args = parser.parse_args()
    
    try:
        if args.command == "active":
            list_active_tasks()
        elif args.command == "scheduled":
            list_scheduled_tasks()
        elif args.command == "failed":
            list_failed_tasks()
        elif args.command == "dlq":
            list_dead_letter_queue()
        elif args.command == "retry":
            if not args.task_id:
                print("Error: --task-id required for retry command")
                sys.exit(1)
            retry_failed_task(args.task_id)
        elif args.command == "metrics":
            get_task_metrics(args.task_name)
        elif args.command == "workers":
            get_worker_stats()
        elif args.command == "purge":
            if not args.queue:
                print("Error: --queue required for purge command")
                sys.exit(1)
            purge_queue(args.queue)
        elif args.command == "restart":
            restart_workers()
            
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
