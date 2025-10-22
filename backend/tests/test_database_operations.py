"""
Database Operations Testing Suite
Tests database integrity, performance, and operations
"""

import pytest
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db, OptimizedQueries, BulkOperations, db_cache
from app.models import User, Project, LogEntry, ChatSession, AuditLog
from app.database.queries import OptimizedQueries
from app.database.bulk_ops import BulkOperations
from app.database.cache import DatabaseCache

class DatabaseTestResults:
    """Store database test results"""
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

# Initialize test results
db_test_results = DatabaseTestResults()

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    start = time.time()
    try:
        async for session in get_db():
            # Test basic connection
            result = await session.execute("SELECT 1")
            elapsed = time.time() - start
            
            db_test_results.add_result(
                "Database Connection",
                "PASS",
                "Database connection successful",
                elapsed
            )
            break
    except Exception as e:
        db_test_results.add_result(
            "Database Connection",
            "FAIL",
            f"Connection failed: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_user_creation():
    """Test user creation and retrieval"""
    start = time.time()
    try:
        async for session in get_db():
            # Create test user
            test_user = User(
                id=str(uuid.uuid4()),
                email="db_test@example.com",
                password_hash="hashed_password",
                full_name="DB Test User",
                subscription_tier="free",
                is_active=True
            )
            
            session.add(test_user)
            await session.commit()
            
            # Retrieve user
            result = await session.execute(
                select(User).where(User.email == "db_test@example.com")
            )
            user = result.scalar_one_or_none()
            
            elapsed = time.time() - start
            
            if user:
                db_test_results.add_result(
                    "User Creation",
                    "PASS",
                    f"User created and retrieved: {user.id}",
                    elapsed
                )
            else:
                db_test_results.add_result(
                    "User Creation",
                    "FAIL",
                    "User not found after creation",
                    elapsed
                )
            break
    except Exception as e:
        db_test_results.add_result(
            "User Creation",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_project_operations():
    """Test project CRUD operations"""
    start = time.time()
    try:
        async for session in get_db():
            # Get test user
            result = await session.execute(
                select(User).where(User.email == "db_test@example.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                db_test_results.add_result(
                    "Project Operations",
                    "FAIL",
                    "Test user not found",
                    time.time() - start
                )
                return
            
            # Create project
            project = Project(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name="DB Test Project",
                description="Test project for database operations"
            )
            
            session.add(project)
            await session.commit()
            
            # Retrieve project
            result = await session.execute(
                select(Project).where(Project.user_id == user.id)
            )
            projects = result.scalars().all()
            
            elapsed = time.time() - start
            
            if projects:
                db_test_results.add_result(
                    "Project Operations",
                    "PASS",
                    f"Project created and retrieved: {len(projects)} projects",
                    elapsed
                )
            else:
                db_test_results.add_result(
                    "Project Operations",
                    "FAIL",
                    "Project not found after creation",
                    elapsed
                )
            break
    except Exception as e:
        db_test_results.add_result(
            "Project Operations",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_bulk_log_insertion():
    """Test bulk log entry insertion"""
    start = time.time()
    try:
        async for session in get_db():
            # Get test project
            result = await session.execute(
                select(Project).where(Project.name == "DB Test Project")
            )
            project = result.scalar_one_or_none()
            
            if not project:
                db_test_results.add_result(
                    "Bulk Log Insertion",
                    "FAIL",
                    "Test project not found",
                    time.time() - start
                )
                return
            
            # Create bulk operations instance
            bulk_ops = BulkOperations(session)
            
            # Generate test log entries
            log_entries = []
            for i in range(100):
                log_entries.append({
                    "id": str(uuid.uuid4()),
                    "user_id": project.user_id,
                    "project_id": project.id,
                    "timestamp": datetime.utcnow() - timedelta(minutes=i),
                    "log_level": ["INFO", "WARN", "ERROR"][i % 3],
                    "message": f"Test log message {i}",
                    "source": "test_source",
                    "metadata": {"test": True, "index": i}
                })
            
            # Insert bulk data
            successful, failed = await bulk_ops.bulk_insert_log_entries(log_entries)
            
            elapsed = time.time() - start
            
            if successful > 0:
                db_test_results.add_result(
                    "Bulk Log Insertion",
                    "PASS",
                    f"Inserted {successful} log entries, {failed} failed",
                    elapsed
                )
            else:
                db_test_results.add_result(
                    "Bulk Log Insertion",
                    "FAIL",
                    f"No entries inserted, {failed} failed",
                    elapsed
                )
            break
    except Exception as e:
        db_test_results.add_result(
            "Bulk Log Insertion",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_query_performance():
    """Test query performance with optimized queries"""
    start = time.time()
    try:
        async for session in get_db():
            # Get test project
            result = await session.execute(
                select(Project).where(Project.name == "DB Test Project")
            )
            project = result.scalar_one_or_none()
            
            if not project:
                db_test_results.add_result(
                    "Query Performance",
                    "FAIL",
                    "Test project not found",
                    time.time() - start
                )
                return
            
            # Test optimized queries
            queries = OptimizedQueries(session)
            
            # Test paginated log entries
            log_data = await queries.get_paginated_log_entries(
                user_id=project.user_id,
                project_id=project.id,
                page=0,
                page_size=50
            )
            
            # Test log level stats
            stats = await queries.get_log_level_stats(project.id)
            
            elapsed = time.time() - start
            
            if log_data and "log_entries" in log_data:
                db_test_results.add_result(
                    "Query Performance",
                    "PASS",
                    f"Retrieved {len(log_data['log_entries'])} log entries, stats: {stats}",
                    elapsed
                )
            else:
                db_test_results.add_result(
                    "Query Performance",
                    "FAIL",
                    "Query returned no data",
                    elapsed
                )
            break
    except Exception as e:
        db_test_results.add_result(
            "Query Performance",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_cache_operations():
    """Test Redis cache operations"""
    start = time.time()
    try:
        # Initialize cache
        await db_cache.initialize()
        
        # Test cache set
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        cache_set_result = await db_cache.set("test_key", test_data, ttl=60)
        
        # Test cache get
        cached_data = await db_cache.get("test_key")
        
        # Test cache hit ratio
        hit_count = 0
        miss_count = 0
        
        for i in range(10):
            result = await db_cache.get(f"test_key_{i}")
            if result is not None:
                hit_count += 1
            else:
                miss_count += 1
        
        elapsed = time.time() - start
        
        if cache_set_result and cached_data:
            hit_ratio = hit_count / (hit_count + miss_count)
            db_test_results.add_result(
                "Cache Operations",
                "PASS",
                f"Cache working, hit ratio: {hit_ratio:.2%}",
                elapsed
            )
        else:
            db_test_results.add_result(
                "Cache Operations",
                "FAIL",
                "Cache operations failed",
                elapsed
            )
    except Exception as e:
        db_test_results.add_result(
            "Cache Operations",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_database_cleanup():
    """Test database cleanup and data integrity"""
    start = time.time()
    try:
        async for session in get_db():
            # Clean up test data
            # Delete log entries
            await session.execute(
                delete(LogEntry).where(LogEntry.message.like("Test log message%"))
            )
            
            # Delete projects
            await session.execute(
                delete(Project).where(Project.name == "DB Test Project")
            )
            
            # Delete test user
            await session.execute(
                delete(User).where(User.email == "db_test@example.com")
            )
            
            await session.commit()
            
            elapsed = time.time() - start
            
            db_test_results.add_result(
                "Database Cleanup",
                "PASS",
                "Test data cleaned up successfully",
                elapsed
            )
            break
    except Exception as e:
        db_test_results.add_result(
            "Database Cleanup",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_generate_database_report():
    """Generate database test report"""
    report = f"""# Database Operations Test Results

**Test Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests:** {len(db_test_results.results)}
**Passed:** {db_test_results.passed} ✅
**Failed:** {db_test_results.failed} ❌
**Warnings:** {db_test_results.warnings} ⚠️
**Success Rate:** {(db_test_results.passed / len(db_test_results.results) * 100):.2f}%

---

## Database Test Results

| Test Name | Status | Response Time | Details |
|-----------|--------|---------------|----------|
"""
    
    for result in db_test_results.results:
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[result['status']]
        report += f"| {result['test']} | {status_icon} {result['status']} | {result['response_time_ms']}ms | {result['details']} |\n"
    
    # Save to file
    with open("DATABASE_TEST_RESULTS.md", "w") as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("DATABASE TEST REPORT GENERATED: DATABASE_TEST_RESULTS.md")
    print("="*60)
    print(f"Total Tests: {len(db_test_results.results)}")
    print(f"Passed: {db_test_results.passed} ✅")
    print(f"Failed: {db_test_results.failed} ❌")
    print(f"Warnings: {db_test_results.warnings} ⚠️")
    print(f"Success Rate: {(db_test_results.passed / len(db_test_results.results) * 100):.2f}%")
    print("="*60 + "\n")
