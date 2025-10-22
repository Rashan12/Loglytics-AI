#!/usr/bin/env python3
"""
Quick Test Runner for Loglytics AI
Runs basic connectivity and health checks
"""

import asyncio
import aiohttp
import time
from datetime import datetime

async def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.get("http://localhost:8000/health") as response:
                elapsed = time.time() - start
                
                if response.status == 200:
                    data = await response.json()
                    print(f"[PASS] Backend Health Check: PASS ({elapsed:.2f}s)")
                    print(f"   Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"[FAIL] Backend Health Check: FAIL ({elapsed:.2f}s)")
                    print(f"   Status Code: {response.status}")
                    return False
    except Exception as e:
        print(f"[ERROR] Backend Health Check: ERROR")
        print(f"   Error: {e}")
        return False

async def test_database_health():
    """Test database health endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.get("http://localhost:8000/database/health") as response:
                elapsed = time.time() - start
                
                if response.status == 200:
                    data = await response.json()
                    print(f"[PASS] Database Health Check: PASS ({elapsed:.2f}s)")
                    print(f"   Database Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"[WARN] Database Health Check: WARN ({elapsed:.2f}s)")
                    print(f"   Status Code: {response.status}")
                    return False
    except Exception as e:
        print(f"[WARN] Database Health Check: WARN")
        print(f"   Error: {e}")
        return False

async def test_security_status():
    """Test security status endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            async with session.get("http://localhost:8000/security/status") as response:
                elapsed = time.time() - start
                
                if response.status == 200:
                    data = await response.json()
                    print(f"[PASS] Security Status Check: PASS ({elapsed:.2f}s)")
                    print(f"   Security Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"[WARN] Security Status Check: WARN ({elapsed:.2f}s)")
                    print(f"   Status Code: {response.status}")
                    return False
    except Exception as e:
        print(f"[WARN] Security Status Check: WARN")
        print(f"   Error: {e}")
        return False

async def test_api_endpoints():
    """Test basic API endpoints"""
    endpoints = [
        ("/", "Root endpoint"),
        ("/docs", "API documentation"),
        ("/api/v1/auth/register", "Auth registration"),
        ("/api/v1/users/me", "User profile (unauthorized)")
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for endpoint, description in endpoints:
            try:
                start = time.time()
                async with session.get(f"http://localhost:8000{endpoint}") as response:
                    elapsed = time.time() - start
                    
                    if response.status in [200, 401, 422]:  # Expected status codes
                        print(f"[PASS] {description}: PASS ({elapsed:.2f}s) - Status: {response.status}")
                        results.append(True)
                    else:
                        print(f"[WARN] {description}: WARN ({elapsed:.2f}s) - Status: {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"[ERROR] {description}: ERROR - {e}")
                results.append(False)
    
    return results

async def main():
    """Main test runner"""
    print("Loglytics AI - Quick Health Check")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run tests
    backend_health = await test_backend_health()
    database_health = await test_database_health()
    security_status = await test_security_status()
    api_results = await test_api_endpoints()
    
    # Summary
    print("\n" + "="*60)
    print("QUICK TEST SUMMARY")
    print("="*60)
    
    total_tests = 3 + len(api_results)
    passed_tests = sum([
        backend_health,
        database_health,
        security_status,
        *api_results
    ])
    
    print(f"Backend Health: {'[PASS] PASS' if backend_health else '[FAIL] FAIL'}")
    print(f"Database Health: {'[PASS] PASS' if database_health else '[WARN] WARN'}")
    print(f"Security Status: {'[PASS] PASS' if security_status else '[WARN] WARN'}")
    print(f"API Endpoints: {sum(api_results)}/{len(api_results)} PASS")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}%)")
    
    if backend_health:
        print("\n[SUCCESS] Backend is running and ready for comprehensive testing!")
        print("Run 'python run_all_tests.py' for full test suite.")
    else:
        print("\n[ERROR] Backend is not running. Please start it first:")
        print("   python -m uvicorn app.main:app --reload")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
