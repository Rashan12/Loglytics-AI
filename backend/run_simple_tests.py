#!/usr/bin/env python3
"""
Simple test runner for Loglytics AI
Runs tests without pytest to avoid dependency conflicts
"""

import asyncio
import time
import json
from datetime import datetime
import aiohttp

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_RESULTS = []

class SimpleTestRunner:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_result(self, test_name, status, details="", response_time=0):
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)

        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "WARN":
            self.warnings += 1

    async def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200):
        """Test a single endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                start = time.time()
                
                if method == "GET":
                    async with session.get(f"{BASE_URL}{endpoint}") as response:
                        elapsed = time.time() - start
                        if response.status == expected_status:
                            self.add_result(f"{method} {endpoint}", "PASS", f"Status: {response.status}", elapsed)
                            return True
                        else:
                            self.add_result(f"{method} {endpoint}", "FAIL", f"Expected {expected_status}, got {response.status}", elapsed)
                            return False
                
                elif method == "POST":
                    async with session.post(f"{BASE_URL}{endpoint}", json=data) as response:
                        elapsed = time.time() - start
                        if response.status == expected_status:
                            self.add_result(f"{method} {endpoint}", "PASS", f"Status: {response.status}", elapsed)
                            return True
                        else:
                            self.add_result(f"{method} {endpoint}", "FAIL", f"Expected {expected_status}, got {response.status}", elapsed)
                            return False
        except Exception as e:
            self.add_result(f"{method} {endpoint}", "FAIL", f"Error: {str(e)}", 0)
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("Loglytics AI - Simple Test Runner")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Basic health tests
        print("\n1. Basic Health Tests")
        print("-" * 30)
        await self.test_endpoint("/", "GET", expected_status=200)
        await self.test_endpoint("/health", "GET", expected_status=200)
        await self.test_endpoint("/database/health", "GET", expected_status=200)
        await self.test_endpoint("/security/status", "GET", expected_status=200)
        
        # API endpoint tests
        print("\n2. API Endpoint Tests")
        print("-" * 30)
        await self.test_endpoint("/api/v1/auth/register", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/users/me", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/projects", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/logs", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/analytics", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/chat", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/llm", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/rag", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/live-logs", "GET", expected_status=200)
        await self.test_endpoint("/api/v1/settings", "GET", expected_status=200)
        
        # Test with POST data
        print("\n3. POST Endpoint Tests")
        print("-" * 30)
        test_user = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "full_name": "Test User"
        }
        await self.test_endpoint("/api/v1/auth/register", "POST", test_user, expected_status=200)
        
        # Performance tests
        print("\n4. Performance Tests")
        print("-" * 30)
        await self.test_endpoint("/health", "GET", expected_status=200)
        await self.test_endpoint("/", "GET", expected_status=200)
        
        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        total_tests = len(self.results)
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Warnings: {self.warnings}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*60)
        
        # Detailed results
        print("\nDETAILED RESULTS")
        print("-" * 60)
        for result in self.results:
            status_icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[result['status']]
            print(f"{status_icon} {result['test']} - {result['response_time_ms']}ms - {result['details']}")
        
        # Generate markdown report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown test report"""
        total_tests = len(self.results)
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""# Loglytics AI - Test Results Report

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Runner:** Simple Test Runner
**Base URL:** {BASE_URL}

## Summary

- **Total Tests:** {total_tests}
- **Passed:** {self.passed} [PASS]
- **Failed:** {self.failed} [FAIL]
- **Warnings:** {self.warnings} [WARN]
- **Success Rate:** {success_rate:.1f}%

## Test Results

| Test Name | Status | Response Time | Details |
|-----------|--------|---------------|---------|
"""
        
        for result in self.results:
            status_icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[result['status']]
            report += f"| {result['test']} | {status_icon} {result['status']} | {result['response_time_ms']}ms | {result['details']} |\n"
        
        report += f"""
## Performance Analysis

- **Average Response Time:** {sum(r['response_time_ms'] for r in self.results) / len(self.results):.2f}ms
- **Fastest Response:** {min(r['response_time_ms'] for r in self.results):.2f}ms
- **Slowest Response:** {max(r['response_time_ms'] for r in self.results):.2f}ms

## Conclusion

{'All tests passed successfully!' if self.failed == 0 else f'{self.failed} tests failed and need attention.'}

---
*Report generated by Simple Test Runner*
"""
        
        # Save report
        with open("SIMPLE_TEST_RESULTS.md", "w") as f:
            f.write(report)
        
        print(f"\n[REPORT] Test report saved to: SIMPLE_TEST_RESULTS.md")

async def main():
    """Main test runner"""
    runner = SimpleTestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
