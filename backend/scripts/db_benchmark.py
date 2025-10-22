#!/usr/bin/env python3
"""
Database Performance Benchmark
Comprehensive performance testing for database operations
"""

import asyncio
import time
import statistics
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta
import random
import string

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import get_db, OptimizedQueries, BulkOperations, db_cache
from app.models import User, Project, LogEntry, ChatSession, ChatMessage
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.orm import selectinload

class DatabaseBenchmark:
    """Database performance benchmark suite"""
    
    def __init__(self):
        self.results = {}
        self.test_data = {}
    
    async def generate_test_data(self, user_count=100, project_count=500, log_count=10000):
        """Generate test data for benchmarking"""
        print("Generating test data...")
        
        # Generate users
        users = []
        for i in range(user_count):
            users.append({
                "id": f"user_{i}",
                "email": f"user{i}@test.com",
                "password_hash": "hashed_password",
                "subscription_tier": "free" if i % 2 == 0 else "pro",
                "is_active": True
            })
        
        # Generate projects
        projects = []
        for i in range(project_count):
            projects.append({
                "id": f"project_{i}",
                "user_id": f"user_{i % user_count}",
                "name": f"Test Project {i}",
                "description": f"Description for project {i}"
            })
        
        # Generate log entries
        log_entries = []
        log_levels = ["ERROR", "WARNING", "INFO", "DEBUG"]
        for i in range(log_count):
            log_entries.append({
                "id": f"log_{i}",
                "user_id": f"user_{i % user_count}",
                "project_id": f"project_{i % project_count}",
                "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 24*30)),
                "log_level": random.choice(log_levels),
                "message": f"Test log message {i}",
                "source": f"test_source_{i % 10}",
                "metadata": {"test": True, "index": i}
            })
        
        self.test_data = {
            "users": users,
            "projects": projects,
            "log_entries": log_entries
        }
        
        print(f"Generated {len(users)} users, {len(projects)} projects, {len(log_entries)} log entries")
    
    async def benchmark_single_queries(self):
        """Benchmark single query operations"""
        print("\n=== Single Query Benchmarks ===")
        
        async for session in get_db():
            queries = OptimizedQueries(session)
            
            # Test 1: Simple select by ID
            times = []
            for i in range(100):
                start = time.time()
                try:
                    result = await session.execute(
                        select(User).where(User.id == f"user_{i % 100}")
                    )
                    result.scalar_one_or_none()
                except:
                    pass
                times.append(time.time() - start)
            
            self.results["single_select_by_id"] = {
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
            print(f"Single select by ID: {statistics.mean(times):.4f}s avg")
            
            # Test 2: Select with joins
            times = []
            for i in range(50):
                start = time.time()
                try:
                    result = await session.execute(
                        select(User)
                        .join(Project)
                        .where(User.id == f"user_{i % 100}")
                        .options(selectinload(User.projects))
                    )
                    result.scalar_one_or_none()
                except:
                    pass
                times.append(time.time() - start)
            
            self.results["select_with_joins"] = {
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
            print(f"Select with joins: {statistics.mean(times):.4f}s avg")
            
            # Test 3: Aggregation queries
            times = []
            for i in range(20):
                start = time.time()
                try:
                    result = await session.execute(
                        select(
                            LogEntry.log_level,
                            func.count(LogEntry.id).label('count')
                        )
                        .where(LogEntry.project_id == f"project_{i % 100}")
                        .group_by(LogEntry.log_level)
                    )
                    list(result)
                except:
                    pass
                times.append(time.time() - start)
            
            self.results["aggregation_queries"] = {
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
            print(f"Aggregation queries: {statistics.mean(times):.4f}s avg")
            
            break
    
    async def benchmark_pagination(self):
        """Benchmark pagination performance"""
        print("\n=== Pagination Benchmarks ===")
        
        async for session in get_db():
            queries = OptimizedQueries(session)
            
            # Test paginated log entries
            times = []
            for page in range(10):
                start = time.time()
                try:
                    result = await queries.get_paginated_log_entries(
                        user_id="user_0",
                        page=page,
                        page_size=100
                    )
                except:
                    pass
                times.append(time.time() - start)
            
            self.results["pagination"] = {
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
            print(f"Pagination (10 pages): {statistics.mean(times):.4f}s avg")
            
            break
    
    async def benchmark_bulk_operations(self):
        """Benchmark bulk operations"""
        print("\n=== Bulk Operations Benchmarks ===")
        
        async for session in get_db():
            bulk_ops = BulkOperations(session)
            
            # Test bulk insert
            test_logs = []
            for i in range(1000):
                test_logs.append({
                    "id": f"bulk_log_{i}",
                    "user_id": "user_0",
                    "project_id": "project_0",
                    "timestamp": datetime.utcnow(),
                    "log_level": "INFO",
                    "message": f"Bulk test message {i}",
                    "source": "benchmark",
                    "metadata": {"bulk_test": True}
                })
            
            start = time.time()
            try:
                successful, failed = await bulk_ops.bulk_insert_log_entries(test_logs)
                bulk_insert_time = time.time() - start
                
                self.results["bulk_insert"] = {
                    "time": bulk_insert_time,
                    "records_per_second": len(test_logs) / bulk_insert_time,
                    "successful": successful,
                    "failed": failed
                }
                print(f"Bulk insert 1000 records: {bulk_insert_time:.4f}s ({len(test_logs)/bulk_insert_time:.0f} records/sec)")
            except Exception as e:
                print(f"Bulk insert failed: {e}")
            
            # Test bulk update
            test_updates = []
            for i in range(100):
                test_updates.append({
                    "id": f"bulk_log_{i}",
                    "metadata": {"updated": True, "timestamp": datetime.utcnow().isoformat()}
                })
            
            start = time.time()
            try:
                successful, failed = await bulk_ops.bulk_update_log_entries(test_updates)
                bulk_update_time = time.time() - start
                
                self.results["bulk_update"] = {
                    "time": bulk_update_time,
                    "records_per_second": len(test_updates) / bulk_update_time,
                    "successful": successful,
                    "failed": failed
                }
                print(f"Bulk update 100 records: {bulk_update_time:.4f}s ({len(test_updates)/bulk_update_time:.0f} records/sec)")
            except Exception as e:
                print(f"Bulk update failed: {e}")
            
            break
    
    async def benchmark_caching(self):
        """Benchmark caching performance"""
        print("\n=== Caching Benchmarks ===")
        
        # Initialize cache
        await db_cache.initialize()
        
        # Test cache set performance
        times = []
        for i in range(100):
            start = time.time()
            await db_cache.set(f"test_key_{i}", {"data": f"test_value_{i}"}, ttl=60)
            times.append(time.time() - start)
        
        self.results["cache_set"] = {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
        print(f"Cache set: {statistics.mean(times):.4f}s avg")
        
        # Test cache get performance
        times = []
        for i in range(100):
            start = time.time()
            await db_cache.get(f"test_key_{i}")
            times.append(time.time() - start)
        
        self.results["cache_get"] = {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
        print(f"Cache get: {statistics.mean(times):.4f}s avg")
        
        # Test cache hit ratio
        hit_count = 0
        miss_count = 0
        
        for i in range(200):
            result = await db_cache.get(f"test_key_{i % 100}")
            if result is not None:
                hit_count += 1
            else:
                miss_count += 1
        
        hit_ratio = hit_count / (hit_count + miss_count)
        self.results["cache_hit_ratio"] = hit_ratio
        print(f"Cache hit ratio: {hit_ratio:.2%}")
    
    async def benchmark_concurrent_operations(self):
        """Benchmark concurrent operations"""
        print("\n=== Concurrent Operations Benchmarks ===")
        
        async def concurrent_query(session, query_id):
            """Execute a concurrent query"""
            start = time.time()
            try:
                result = await session.execute(
                    select(LogEntry)
                    .where(LogEntry.user_id == f"user_{query_id % 100}")
                    .limit(10)
                )
                list(result)
            except:
                pass
            return time.time() - start
        
        # Test concurrent queries
        times = []
        tasks = []
        
        async for session in get_db():
            for i in range(50):
                task = asyncio.create_task(concurrent_query(session, i))
                tasks.append(task)
            
            start = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start
            
            # Filter out exceptions
            valid_times = [r for r in results if isinstance(r, (int, float))]
            
            self.results["concurrent_queries"] = {
                "total_time": total_time,
                "queries_per_second": len(valid_times) / total_time,
                "avg_query_time": statistics.mean(valid_times) if valid_times else 0,
                "successful_queries": len(valid_times),
                "failed_queries": len(results) - len(valid_times)
            }
            print(f"Concurrent queries (50): {total_time:.4f}s total ({len(valid_times)/total_time:.0f} queries/sec)")
            break
    
    async def run_all_benchmarks(self):
        """Run all benchmark tests"""
        print("Starting database performance benchmarks...")
        
        # Generate test data
        await self.generate_test_data()
        
        # Run individual benchmarks
        await self.benchmark_single_queries()
        await self.benchmark_pagination()
        await self.benchmark_bulk_operations()
        await self.benchmark_caching()
        await self.benchmark_concurrent_operations()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate benchmark summary"""
        print("\n=== Benchmark Summary ===")
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "results": self.results
        }
        
        # Save results to file
        results_file = Path("benchmark_results.json")
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"Results saved to {results_file}")
        
        # Print key metrics
        if "single_select_by_id" in self.results:
            print(f"Single select performance: {self.results['single_select_by_id']['avg_time']:.4f}s")
        
        if "bulk_insert" in self.results:
            print(f"Bulk insert performance: {self.results['bulk_insert']['records_per_second']:.0f} records/sec")
        
        if "concurrent_queries" in self.results:
            print(f"Concurrent query performance: {self.results['concurrent_queries']['queries_per_second']:.0f} queries/sec")
        
        if "cache_hit_ratio" in self.results:
            print(f"Cache hit ratio: {self.results['cache_hit_ratio']:.2%}")

async def main():
    """Main benchmark function"""
    benchmark = DatabaseBenchmark()
    await benchmark.run_all_benchmarks()

if __name__ == "__main__":
    asyncio.run(main())
