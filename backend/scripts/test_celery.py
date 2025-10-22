#!/usr/bin/env python3
"""
Test script for Celery setup
Verifies that all Celery tasks work correctly
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.celery_app import celery_app
from app.tasks import (
    process_log_file, generate_embeddings, cleanup_old_logs, compress_log_file,
    calculate_analytics, update_project_analytics, generate_analytics_report, detect_anomalies,
    poll_cloud_logs, process_live_logs, check_alert_conditions, send_alerts,
    send_email, send_slack_notification, create_jira_ticket, send_in_app_notification,
    cleanup_expired_api_keys, update_usage_statistics, backup_database, health_check
)


def test_task_execution(task_func, task_name, *args, **kwargs):
    """Test a single task execution"""
    print(f"Testing {task_name}...")
    
    try:
        # Queue the task
        result = task_func.delay(*args, **kwargs)
        
        # Wait for result with timeout
        try:
            task_result = result.get(timeout=30)
            print(f"  ✓ {task_name} completed successfully")
            print(f"  Result: {json.dumps(task_result, indent=2)}")
            return True
        except Exception as e:
            print(f"  ✗ {task_name} failed: {e}")
            return False
            
    except Exception as e:
        print(f"  ✗ {task_name} failed to queue: {e}")
        return False


def test_log_processing_tasks():
    """Test log processing tasks"""
    print("\n=== Testing Log Processing Tasks ===")
    
    test_file_id = "test_log_file_123"
    
    tasks = [
        (process_log_file, "Process Log File", test_file_id),
        (generate_embeddings, "Generate Embeddings", test_file_id),
        (cleanup_old_logs, "Cleanup Old Logs", 30),
        (compress_log_file, "Compress Log File", test_file_id),
    ]
    
    results = []
    for task_func, task_name, *args in tasks:
        results.append(test_task_execution(task_func, task_name, *args))
    
    return all(results)


def test_analytics_tasks():
    """Test analytics tasks"""
    print("\n=== Testing Analytics Tasks ===")
    
    test_file_id = "test_log_file_123"
    test_project_id = "test_project_456"
    test_email = "test@example.com"
    
    tasks = [
        (calculate_analytics, "Calculate Analytics", test_file_id),
        (update_project_analytics, "Update Project Analytics", test_project_id),
        (generate_analytics_report, "Generate Analytics Report", test_project_id, test_email),
        (detect_anomalies, "Detect Anomalies", test_file_id),
    ]
    
    results = []
    for task_func, task_name, *args in tasks:
        results.append(test_task_execution(task_func, task_name, *args))
    
    return all(results)


def test_live_stream_tasks():
    """Test live stream tasks"""
    print("\n=== Testing Live Stream Tasks ===")
    
    test_connection_id = "test_connection_789"
    test_logs_batch = [
        {"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "message": "Test log 1"},
        {"timestamp": "2024-01-01T10:01:00Z", "level": "ERROR", "message": "Test log 2"},
    ]
    test_alert_ids = ["alert_1", "alert_2"]
    
    tasks = [
        (poll_cloud_logs, "Poll Cloud Logs", test_connection_id),
        (process_live_logs, "Process Live Logs", test_connection_id, test_logs_batch),
        (check_alert_conditions, "Check Alert Conditions", test_connection_id),
        (send_alerts, "Send Alerts", test_alert_ids),
    ]
    
    results = []
    for task_func, task_name, *args in tasks:
        results.append(test_task_execution(task_func, task_name, *args))
    
    return all(results)


def test_notification_tasks():
    """Test notification tasks"""
    print("\n=== Testing Notification Tasks ===")
    
    test_email = "test@example.com"
    test_subject = "Test Email"
    test_body = "This is a test email"
    test_webhook_url = "https://hooks.slack.com/test"
    test_message = "Test Slack message"
    test_project_key = "TEST"
    test_summary = "Test Jira Ticket"
    test_description = "This is a test Jira ticket"
    test_user_id = "test_user_123"
    test_notification_data = {
        "title": "Test Notification",
        "message": "This is a test notification",
        "type": "info"
    }
    
    tasks = [
        (send_email, "Send Email", test_email, test_subject, test_body),
        (send_slack_notification, "Send Slack Notification", test_webhook_url, test_message),
        (create_jira_ticket, "Create Jira Ticket", test_project_key, test_summary, test_description),
        (send_in_app_notification, "Send In-App Notification", test_user_id, test_notification_data),
    ]
    
    results = []
    for task_func, task_name, *args in tasks:
        results.append(test_task_execution(task_func, task_name, *args))
    
    return all(results)


def test_maintenance_tasks():
    """Test maintenance tasks"""
    print("\n=== Testing Maintenance Tasks ===")
    
    tasks = [
        (cleanup_expired_api_keys, "Cleanup Expired API Keys"),
        (update_usage_statistics, "Update Usage Statistics"),
        (backup_database, "Backup Database"),
        (health_check, "Health Check"),
    ]
    
    results = []
    for task_func, task_name in tasks:
        results.append(test_task_execution(task_func, task_name))
    
    return all(results)


def test_periodic_tasks():
    """Test periodic tasks"""
    print("\n=== Testing Periodic Tasks ===")
    
    # Test periodic tasks that can be triggered manually
    from app.tasks.live_stream_tasks import poll_all_connections, check_all_alert_conditions
    from app.tasks.analytics_tasks import update_all_project_analytics, generate_weekly_reports
    
    tasks = [
        (poll_all_connections, "Poll All Connections"),
        (check_all_alert_conditions, "Check All Alert Conditions"),
        (update_all_project_analytics, "Update All Project Analytics"),
        (generate_weekly_reports, "Generate Weekly Reports"),
    ]
    
    results = []
    for task_func, task_name in tasks:
        results.append(test_task_execution(task_func, task_name))
    
    return all(results)


def test_celery_connectivity():
    """Test Celery connectivity and configuration"""
    print("\n=== Testing Celery Connectivity ===")
    
    try:
        # Test broker connectivity
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print(f"  ✓ Connected to {len(stats)} workers")
            for worker in stats:
                print(f"    - {worker}: {stats[worker].get('status', 'Unknown')}")
        else:
            print("  ⚠ No workers found (this is expected if workers aren't running)")
            
        # Test task registration
        registered_tasks = list(celery_app.tasks.keys())
        print(f"  ✓ {len(registered_tasks)} tasks registered")
        
        # Test beat schedule
        beat_schedule = celery_app.conf.beat_schedule
        print(f"  ✓ {len(beat_schedule)} periodic tasks configured")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Celery connectivity test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and retry mechanisms"""
    print("\n=== Testing Error Handling ===")
    
    # Create a test task that will fail
    @celery_app.task(bind=True, max_retries=2)
    def failing_task(self):
        raise Exception("This task is designed to fail")
    
    try:
        result = failing_task.delay()
        
        # Wait for the task to fail and retry
        try:
            result.get(timeout=60)
        except Exception as e:
            print(f"  ✓ Task failed as expected: {e}")
            
        # Check if task was retried
        if result.retries > 0:
            print(f"  ✓ Task was retried {result.retries} times")
        else:
            print("  ⚠ Task was not retried (may have failed immediately)")
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False


def main():
    """Main test function"""
    print("Celery Setup Test Suite")
    print("=" * 50)
    
    # Test connectivity first
    if not test_celery_connectivity():
        print("\n❌ Celery connectivity test failed. Please check your configuration.")
        return False
    
    # Run all task tests
    test_results = []
    
    test_results.append(("Log Processing Tasks", test_log_processing_tasks()))
    test_results.append(("Analytics Tasks", test_analytics_tasks()))
    test_results.append(("Live Stream Tasks", test_live_stream_tasks()))
    test_results.append(("Notification Tasks", test_notification_tasks()))
    test_results.append(("Maintenance Tasks", test_maintenance_tasks()))
    test_results.append(("Periodic Tasks", test_periodic_tasks()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Celery setup is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration and try again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
