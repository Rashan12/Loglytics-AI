#!/usr/bin/env python3
"""
Management script to stop Celery workers and beat scheduler
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


def find_celery_processes():
    """Find running Celery processes"""
    try:
        # Find processes by name
        result = subprocess.run(
            ["pgrep", "-f", "celery.*app.celery_app"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid]
        return []
    except Exception as e:
        print(f"Error finding Celery processes: {e}")
        return []


def stop_processes(pids, signal_type=signal.SIGTERM):
    """Stop processes by PID"""
    stopped = []
    for pid in pids:
        try:
            os.kill(pid, signal_type)
            stopped.append(pid)
            print(f"Sent signal {signal_type} to process {pid}")
        except ProcessLookupError:
            print(f"Process {pid} not found")
        except PermissionError:
            print(f"Permission denied to stop process {pid}")
        except Exception as e:
            print(f"Error stopping process {pid}: {e}")
    
    return stopped


def force_kill_processes(pids):
    """Force kill processes that didn't stop gracefully"""
    print("Force killing remaining processes...")
    return stop_processes(pids, signal.SIGKILL)


def main():
    """Main function to stop all Celery services"""
    print("Stopping Celery services...")
    
    # Find running Celery processes
    pids = find_celery_processes()
    
    if not pids:
        print("No Celery processes found")
        return 0
    
    print(f"Found {len(pids)} Celery processes: {pids}")
    
    # Send TERM signal first
    stopped = stop_processes(pids, signal.SIGTERM)
    
    if stopped:
        print("Waiting for processes to stop gracefully...")
        time.sleep(5)
        
        # Check if processes are still running
        remaining_pids = find_celery_processes()
        if remaining_pids:
            print(f"Some processes still running: {remaining_pids}")
            force_kill_processes(remaining_pids)
        else:
            print("All processes stopped gracefully")
    else:
        print("No processes were stopped")
    
    print("Celery services stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
