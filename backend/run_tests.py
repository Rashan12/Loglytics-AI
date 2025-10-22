#!/usr/bin/env python3
"""
Test runner script for Loglytics AI analytics tests
"""

import subprocess
import sys
import os

def run_tests():
    """Run the analytics tests"""
    print("🧪 Running Loglytics AI Analytics Tests...")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with verbose output
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_analytics.py", 
        "-v", 
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r requirements-test.txt")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
