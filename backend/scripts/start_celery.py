#!/usr/bin/env python3
"""
Management script to start Celery workers and beat scheduler
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings


def start_worker(queues="high-priority,default,low-priority", concurrency=4, loglevel="info"):
    """Start Celery worker"""
    cmd = [
        "celery", "-A", "app.celery_app", "worker",
        "--loglevel", loglevel,
        "--concurrency", str(concurrency),
        "--queues", queues
    ]
    
    print(f"Starting Celery worker with queues: {queues}, concurrency: {concurrency}")
    return subprocess.Popen(cmd)


def start_beat():
    """Start Celery beat scheduler"""
    cmd = [
        "celery", "-A", "app.celery_app", "beat",
        "--loglevel", "info",
        "--scheduler", "celery.beat:PersistentScheduler"
    ]
    
    print("Starting Celery beat scheduler")
    return subprocess.Popen(cmd)


def start_flower(port=5555):
    """Start Celery Flower monitoring"""
    cmd = [
        "celery", "-A", "app.celery_app", "flower",
        "--port", str(port)
    ]
    
    print(f"Starting Celery Flower on port {port}")
    return subprocess.Popen(cmd)


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nShutting down Celery processes...")
    for process in processes:
        if process.poll() is None:
            process.terminate()
    sys.exit(0)


def main():
    """Main function to start all Celery services"""
    global processes
    processes = []
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start worker
        worker = start_worker()
        processes.append(worker)
        
        # Start beat scheduler
        beat = start_beat()
        processes.append(beat)
        
        # Start Flower (optional)
        if os.getenv("START_FLOWER", "false").lower() == "true":
            flower = start_flower()
            processes.append(flower)
        
        print("All Celery services started. Press Ctrl+C to stop.")
        
        # Wait for processes
        while True:
            time.sleep(1)
            for process in processes:
                if process.poll() is not None:
                    print(f"Process {process.pid} exited with code {process.returncode}")
                    return process.returncode
                    
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Clean up processes
        for process in processes:
            if process.poll() is None:
                process.terminate()
                process.wait()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
