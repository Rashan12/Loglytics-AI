from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.models import LogEntry, LogLevel
from collections import defaultdict
import re

class PerformanceAnalyzer:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_performance(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method to analyze performance metrics from logs
        Orchestrates all performance analysis components
        """
        # Get log entries for analysis
        log_entries = await self._get_log_entries(project_id, log_file_id)
        
        if not log_entries:
            return {
                "response_time_analysis": {},
                "throughput_metrics": {},
                "slow_operations": [],
                "endpoint_performance": [],
                "resource_usage": {},
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Analyze different performance aspects
        response_time_analysis = self._extract_response_times(log_entries)
        throughput_metrics = self._calculate_throughput(log_entries)
        slow_operations = self._detect_slow_operations(log_entries)
        endpoint_performance = self._analyze_endpoint_performance(log_entries)
        resource_usage = self._analyze_resource_usage(log_entries)
        
        return {
            "response_time_analysis": response_time_analysis,
            "throughput_metrics": throughput_metrics,
            "slow_operations": slow_operations,
            "endpoint_performance": endpoint_performance,
            "resource_usage": resource_usage,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _get_log_entries(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get log entries for analysis"""
        query = select(
            LogEntry.timestamp,
            LogEntry.log_level,
            LogEntry.message,
            LogEntry.source,
            LogEntry.metadata
        ).filter(
            LogEntry.project_id == project_id
        ).order_by(LogEntry.timestamp)
        
        if log_file_id:
            query = query.filter(LogEntry.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "timestamp": row.timestamp,
                "log_level": row.log_level,
                "message": row.message,
                "source": row.source,
                "metadata": row.metadata or {}
            }
            for row in rows
        ]
    
    def _extract_response_times(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract response times from log messages using regex patterns
        Calculate min, max, avg, median, p95, p99 and create histogram
        """
        # Regex patterns for response time extraction
        patterns = [
            r'(?:response|took|duration)[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)',
            r'(\d+\.?\d*)\s*ms',
            r'completed in (\d+\.?\d*)\s*(?:ms|milliseconds)',
            r'execution time[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)',
            r'processing time[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)'
        ]
        
        response_times = []
        
        for entry in log_entries:
            message = entry["message"].lower()
            
            # Try each pattern
            for pattern in patterns:
                matches = re.findall(pattern, message)
                for match in matches:
                    try:
                        time_ms = float(match)
                        if 0 < time_ms < 300000:  # Reasonable range: 0-5 minutes
                            response_times.append(time_ms)
                    except ValueError:
                        continue
        
        if not response_times:
            return {
                "count": 0,
                "min": 0,
                "max": 0,
                "avg": 0,
                "median": 0,
                "p95": 0,
                "p99": 0,
                "histogram": []
            }
        
        # Calculate statistics
        response_times.sort()
        count = len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        avg_time = sum(response_times) / count
        
        # Calculate percentiles
        median = self._calculate_percentile(response_times, 50)
        p95 = self._calculate_percentile(response_times, 95)
        p99 = self._calculate_percentile(response_times, 99)
        
        # Create histogram (10 buckets)
        histogram = self._create_histogram(response_times, 10)
        
        return {
            "count": count,
            "min": round(min_time, 2),
            "max": round(max_time, 2),
            "avg": round(avg_time, 2),
            "median": round(median, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "histogram": histogram
        }
    
    def _calculate_throughput(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate throughput metrics (logs per minute/second)
        Group logs by minute and analyze distribution
        """
        if not log_entries:
            return {
                "logs_per_minute": {"min": 0, "max": 0, "avg": 0},
                "estimated_logs_per_second": 0,
                "peak_minute": {"timestamp": None, "count": 0},
                "throughput_timeline": []
            }
        
        # Group logs by minute
        minute_counts = defaultdict(int)
        for entry in log_entries:
            minute_key = entry["timestamp"].replace(second=0, microsecond=0)
            minute_counts[minute_key] += 1
        
        if not minute_counts:
            return {
                "logs_per_minute": {"min": 0, "max": 0, "avg": 0},
                "estimated_logs_per_second": 0,
                "peak_minute": {"timestamp": None, "count": 0},
                "throughput_timeline": []
            }
        
        counts = list(minute_counts.values())
        min_count = min(counts)
        max_count = max(counts)
        avg_count = sum(counts) / len(counts)
        
        # Find peak minute
        peak_minute = max(minute_counts.items(), key=lambda x: x[1])
        
        # Create timeline for visualization
        timeline = []
        for minute, count in sorted(minute_counts.items()):
            timeline.append({
                "timestamp": minute.isoformat(),
                "count": count
            })
        
        return {
            "logs_per_minute": {
                "min": min_count,
                "max": max_count,
                "avg": round(avg_count, 2)
            },
            "estimated_logs_per_second": round(avg_count / 60, 2),
            "peak_minute": {
                "timestamp": peak_minute[0].isoformat(),
                "count": peak_minute[1]
            },
            "throughput_timeline": timeline
        }
    
    def _detect_slow_operations(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect slow database queries and operations
        Find patterns indicating slow operations and extract durations
        """
        slow_operations = []
        
        # Patterns for slow operations
        slow_patterns = [
            r'slow query[:\s]+(.+?)[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)',
            r'query took[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)[:\s]+(.+)',
            r'timeout[:\s]+(.+?)[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)',
            r'operation[:\s]+(.+?)[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)',
            r'execution[:\s]+(.+?)[:\s]+(\d+\.?\d*)\s*(?:ms|milliseconds)'
        ]
        
        for entry in log_entries:
            message = entry["message"].lower()
            
            for pattern in slow_patterns:
                matches = re.findall(pattern, message)
                for match in matches:
                    try:
                        if len(match) == 2:
                            duration, operation = match
                        else:
                            operation, duration = match
                        
                        duration_ms = float(duration)
                        
                        # Flag operations >1000ms
                        if duration_ms > 1000:
                            slow_operations.append({
                                "operation": operation.strip()[:100],
                                "duration_ms": round(duration_ms, 2),
                                "timestamp": entry["timestamp"].isoformat(),
                                "source": entry["source"] or "Unknown",
                                "log_level": entry["log_level"],
                                "severity": "critical" if duration_ms > 10000 else "high" if duration_ms > 5000 else "medium"
                            })
                    except (ValueError, IndexError):
                        continue
        
        # Return top 20 slowest operations
        return sorted(slow_operations, key=lambda x: x["duration_ms"], reverse=True)[:20]
    
    def _analyze_endpoint_performance(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze API endpoint performance
        Extract endpoints and response times, calculate performance scores
        """
        # Pattern to extract HTTP method, endpoint, and response time
        endpoint_pattern = r'(?:GET|POST|PUT|DELETE|PATCH)\s+([^\s]+).*?(\d+\.?\d*)\s*ms'
        
        endpoint_data = defaultdict(lambda: {
            "response_times": [],
            "error_count": 0,
            "total_requests": 0,
            "methods": set()
        })
        
        for entry in log_entries:
            message = entry["message"]
            
            # Extract endpoint and response time
            matches = re.findall(endpoint_pattern, message)
            for endpoint, response_time_str in matches:
                try:
                    response_time = float(response_time_str)
                    if 0 < response_time < 300000:  # Reasonable range
                        endpoint_data[endpoint]["response_times"].append(response_time)
                        endpoint_data[endpoint]["total_requests"] += 1
                        
                        # Extract HTTP method
                        method_match = re.search(r'(GET|POST|PUT|DELETE|PATCH)', message)
                        if method_match:
                            endpoint_data[endpoint]["methods"].add(method_match.group(1))
                        
                        # Count errors
                        if entry["log_level"] in ["ERROR", "CRITICAL"]:
                            endpoint_data[endpoint]["error_count"] += 1
                            
                except ValueError:
                    continue
        
        # Calculate performance metrics for each endpoint
        endpoint_performance = []
        for endpoint, data in endpoint_data.items():
            if not data["response_times"]:
                continue
            
            response_times = data["response_times"]
            avg_response_time = sum(response_times) / len(response_times)
            error_rate = data["error_count"] / data["total_requests"] if data["total_requests"] > 0 else 0
            
            # Performance score: (1 - error_rate) * (1000 / (avg_time + 1))
            performance_score = (1 - error_rate) * (1000 / (avg_response_time + 1))
            
            endpoint_performance.append({
                "endpoint": endpoint,
                "methods": list(data["methods"]),
                "total_requests": data["total_requests"],
                "avg_response_time_ms": round(avg_response_time, 2),
                "error_rate": round(error_rate, 3),
                "performance_score": round(performance_score, 2),
                "error_count": data["error_count"]
            })
        
        # Return top 15 endpoints by performance score
        return sorted(endpoint_performance, key=lambda x: x["performance_score"], reverse=True)[:15]
    
    def _analyze_resource_usage(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze resource usage patterns (CPU, memory)
        Extract CPU and memory usage from log messages
        """
        cpu_values = []
        memory_values = []
        
        # Patterns for resource extraction
        cpu_patterns = [
            r'cpu[:\s]+(\d+\.?\d*)%?',
            r'cpu usage[:\s]+(\d+\.?\d*)%?',
            r'cpu load[:\s]+(\d+\.?\d*)%?'
        ]
        
        memory_patterns = [
            r'memory[:\s]+(\d+\.?\d*)\s*(?:mb|gb|%)?',
            r'memory usage[:\s]+(\d+\.?\d*)\s*(?:mb|gb|%)?',
            r'ram[:\s]+(\d+\.?\d*)\s*(?:mb|gb|%)?'
        ]
        
        for entry in log_entries:
            message = entry["message"].lower()
            
            # Extract CPU values
            for pattern in cpu_patterns:
                matches = re.findall(pattern, message)
                for match in matches:
                    try:
                        cpu_value = float(match)
                        if 0 <= cpu_value <= 100:  # CPU percentage
                            cpu_values.append(cpu_value)
                    except ValueError:
                        continue
            
            # Extract memory values
            for pattern in memory_patterns:
                matches = re.findall(pattern, message)
                for match in matches:
                    try:
                        memory_value = float(match)
                        if 0 <= memory_value <= 100:  # Assume percentage
                            memory_values.append(memory_value)
                    except ValueError:
                        continue
        
        # Calculate statistics
        cpu_stats = self._calculate_resource_stats(cpu_values, "CPU")
        memory_stats = self._calculate_resource_stats(memory_values, "Memory")
        
        return {
            "cpu": cpu_stats,
            "memory": memory_stats
        }
    
    def _calculate_resource_stats(
        self,
        values: List[float],
        resource_name: str
    ) -> Dict[str, Any]:
        """Calculate statistics for resource usage"""
        if not values:
            return {
                "count": 0,
                "min": 0,
                "max": 0,
                "avg": 0,
                "median": 0
            }
        
        values.sort()
        count = len(values)
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / count
        median_val = self._calculate_percentile(values, 50)
        
        return {
            "count": count,
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "avg": round(avg_val, 2),
            "median": round(median_val, 2)
        }
    
    def _calculate_percentile(
        self,
        values: List[float],
        percentile: int
    ) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _create_histogram(
        self,
        values: List[float],
        buckets: int
    ) -> List[Dict[str, Any]]:
        """Create histogram distribution"""
        if not values:
            return []
        
        min_val = min(values)
        max_val = max(values)
        bucket_size = (max_val - min_val) / buckets if max_val > min_val else 1
        
        histogram = []
        for i in range(buckets):
            bucket_start = min_val + i * bucket_size
            bucket_end = min_val + (i + 1) * bucket_size
            
            count = sum(1 for val in values if bucket_start <= val < bucket_end)
            if i == buckets - 1:  # Last bucket includes max value
                count = sum(1 for val in values if bucket_start <= val <= bucket_end)
            
            histogram.append({
                "bucket": f"{bucket_start:.1f}-{bucket_end:.1f}",
                "count": count,
                "start": round(bucket_start, 1),
                "end": round(bucket_end, 1)
            })
        
        return histogram
