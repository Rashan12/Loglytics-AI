#!/usr/bin/env python3
"""
Comprehensive Test Runner for Loglytics AI
Runs all test suites and generates comprehensive reports
"""

import asyncio
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    # Prevent third-party pytest plugins from auto-loading (fixes eth_typing/web3 plugin errors on Windows)
    os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[PASS] {description} completed successfully ({elapsed:.2f}s)")
            return True, result.stdout, result.stderr
        else:
            print(f"[FAIL] {description} failed ({elapsed:.2f}s)")
            print(f"Error: {result.stderr}")
            return False, result.stdout, result.stderr
    except Exception as e:
        print(f"[ERROR] {description} failed with exception: {e}")
        return False, "", str(e)

def check_backend_running():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test runner"""
    print("Loglytics AI - Comprehensive Test Suite")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check if backend is running
    if not check_backend_running():
        print("[ERROR] Backend is not running!")
        print("Please start the backend first:")
        print("  python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("[PASS] Backend is running")
    
    # Install test dependencies
    success, stdout, stderr = run_command(
        "pip install -r requirements-test.txt",
        "Installing test dependencies"
    )
    
    if not success:
        print("[ERROR] Failed to install test dependencies")
        sys.exit(1)
    
    # Test results
    test_results = {
        "end_to_end": False,
        "database": False,
        "websocket": False,
        "coverage": False
    }
    
    # Run End-to-End Tests
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_end_to_end.py -v -s --tb=short",
        "End-to-End API Tests"
    )
    test_results["end_to_end"] = success
    
    # Run Database Tests
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_database_operations.py -v -s --tb=short",
        "Database Operations Tests"
    )
    test_results["database"] = success
    
    # Run WebSocket Tests
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_websocket_connections.py -v -s --tb=short",
        "WebSocket Connection Tests"
    )
    test_results["websocket"] = success
    
    # Run Coverage Analysis
    success, stdout, stderr = run_command(
        "python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v",
        "Code Coverage Analysis"
    )
    test_results["coverage"] = success
    
    # Generate comprehensive report
    generate_comprehensive_report(test_results)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, passed in test_results.items():
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests*100):.1f}%)")
    
    if passed_tests == total_tests:
        print("[SUCCESS] All tests passed!")
    else:
        print("[WARNING] Some tests failed. Check the individual reports for details.")
    
    print("\nGenerated Reports:")
    print("- TEST_RESULTS.md (End-to-End Tests)")
    print("- DATABASE_TEST_RESULTS.md (Database Tests)")
    print("- WEBSOCKET_TEST_RESULTS.md (WebSocket Tests)")
    print("- htmlcov/index.html (Code Coverage)")
    print("- COMPREHENSIVE_TEST_REPORT.md (Combined Report)")
    
    print("="*80)

def generate_comprehensive_report(test_results):
    """Generate comprehensive test report"""
    report = f"""# Loglytics AI - Comprehensive Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Suite:** Complete Backend Testing

## Executive Summary

This report contains the results of comprehensive testing for the Loglytics AI backend application, including API endpoints, database operations, WebSocket connections, and code coverage analysis.

## Test Suite Results

| Test Suite | Status | Description |
|------------|--------|-------------|
| End-to-End API Tests | {'[PASS] PASS' if test_results['end_to_end'] else '[FAIL] FAIL'} | Complete API endpoint testing |
| Database Operations | {'[PASS] PASS' if test_results['database'] else '[FAIL] FAIL'} | Database integrity and performance |
| WebSocket Connections | {'[PASS] PASS' if test_results['websocket'] else '[FAIL] FAIL'} | Real-time communication testing |
| Code Coverage | {'[PASS] PASS' if test_results['coverage'] else '[FAIL] FAIL'} | Code coverage analysis |

## Detailed Reports

### 1. End-to-End API Tests
- **File:** TEST_RESULTS.md
- **Scope:** Authentication, Projects, Log Processing, AI Analysis, RAG Search, Analytics
- **Coverage:** All major API endpoints and business logic

### 2. Database Operations Tests
- **File:** DATABASE_TEST_RESULTS.md
- **Scope:** Database connections, CRUD operations, bulk operations, query performance
- **Coverage:** Database integrity and optimization features

### 3. WebSocket Connection Tests
- **File:** WEBSOCKET_TEST_RESULTS.md
- **Scope:** Real-time notifications, live logs, chat functionality
- **Coverage:** WebSocket connections and message handling

### 4. Code Coverage Analysis
- **File:** htmlcov/index.html
- **Scope:** Complete codebase coverage analysis
- **Coverage:** Lines, branches, and functions covered

## Test Environment

- **Backend URL:** http://localhost:8000
- **WebSocket URL:** ws://localhost:8000
- **Database:** PostgreSQL (configured)
- **Cache:** Redis (configured)
- **Test Framework:** pytest with asyncio support

## Recommendations

Based on the test results, the following recommendations are made:

1. **API Testing:** Ensure all endpoints return expected responses
2. **Database Testing:** Verify data integrity and performance
3. **WebSocket Testing:** Confirm real-time features work correctly
4. **Coverage Analysis:** Aim for >80% code coverage
5. **Performance Testing:** Monitor response times and resource usage

## Next Steps

1. Review individual test reports for detailed findings
2. Address any failing tests
3. Improve code coverage where needed
4. Set up continuous integration with these tests
5. Implement automated testing in deployment pipeline

---

*This report was generated automatically by the Loglytics AI test suite.*
"""
    
    with open("COMPREHENSIVE_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    print(f"\n[REPORT] Comprehensive report generated: COMPREHENSIVE_TEST_REPORT.md")

if __name__ == "__main__":
    main()
