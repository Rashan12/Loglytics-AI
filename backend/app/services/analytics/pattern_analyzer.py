from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models import LogEntry, LogLevel
from collections import defaultdict, Counter
import re

class PatternAnalyzer:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_patterns(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method to analyze patterns in log messages
        Focuses on ERROR, CRITICAL, and WARN logs only
        """
        # Get error/warning log entries for analysis
        log_entries = await self._get_error_log_entries(project_id, log_file_id)
        
        if not log_entries:
            return {
                "total_analyzed": 0,
                "common_patterns": [],
                "potential_root_causes": [],
                "error_correlations": [],
                "message_clusters": [],
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Analyze different pattern aspects
        common_patterns = self._extract_common_patterns(log_entries)
        potential_root_causes = self._analyze_root_causes(log_entries)
        error_correlations = self._find_error_correlations(log_entries)
        message_clusters = self._cluster_messages(log_entries)
        
        return {
            "total_analyzed": len(log_entries),
            "common_patterns": common_patterns,
            "potential_root_causes": potential_root_causes,
            "error_correlations": error_correlations,
            "message_clusters": message_clusters,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _get_error_log_entries(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get ERROR, CRITICAL, and WARN log entries for analysis"""
        query = select(
            LogEntry.timestamp,
            LogEntry.log_level,
            LogEntry.message,
            LogEntry.source
        ).filter(
            LogEntry.project_id == project_id,
            LogEntry.log_level.in_(['ERROR', 'CRITICAL', 'WARN'])
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
                "source": row.source
            }
            for row in rows
        ]
    
    def _extract_common_patterns(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract common error patterns from messages
        Tokenize and create 2-word and 3-word patterns
        """
        if not log_entries:
            return []
        
        # Tokenize messages and create patterns
        patterns_2gram = Counter()
        patterns_3gram = Counter()
        total_messages = len(log_entries)
        
        for entry in log_entries:
            message = entry["message"].lower()
            
            # Tokenize: extract words with 3+ characters
            tokens = re.findall(r'\b[a-zA-Z]{3,}\b', message)
            
            # Create 2-gram patterns
            for i in range(len(tokens) - 1):
                pattern = f"{tokens[i]} {tokens[i+1]}"
                patterns_2gram[pattern] += 1
            
            # Create 3-gram patterns
            for i in range(len(tokens) - 2):
                pattern = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
                patterns_3gram[pattern] += 1
        
        # Combine and filter patterns
        all_patterns = patterns_2gram + patterns_3gram
        
        # Filter patterns appearing >2 times
        filtered_patterns = {
            pattern: count for pattern, count in all_patterns.items() 
            if count > 2
        }
        
        # Calculate frequency percentages and create results
        common_patterns = []
        for pattern, count in Counter(filtered_patterns).most_common(15):
            frequency_percent = (count / total_messages) * 100
            common_patterns.append({
                "pattern": pattern,
                "count": count,
                "frequency_percent": round(frequency_percent, 2),
                "type": "2-gram" if len(pattern.split()) == 2 else "3-gram"
            })
        
        return common_patterns
    
    def _analyze_root_causes(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze potential root causes using keyword categories
        Match error messages to predefined cause categories
        """
        if not log_entries:
            return []
        
        # Define root cause categories with keywords
        root_cause_categories = {
            "connection_issues": [
                "connection refused", "connection timeout", "connection failed",
                "cannot connect", "connection reset", "connection lost",
                "unable to connect", "connection error"
            ],
            "permission_issues": [
                "permission denied", "access denied", "forbidden",
                "unauthorized", "insufficient permissions", "access control",
                "not authorized", "permission error"
            ],
            "resource_exhaustion": [
                "out of memory", "disk full", "no space left",
                "memory exhausted", "resource limit", "quota exceeded",
                "insufficient resources", "memory allocation failed"
            ],
            "configuration_errors": [
                "config error", "invalid configuration", "configuration failed",
                "missing config", "invalid setting", "config not found",
                "configuration error", "invalid parameter"
            ],
            "database_issues": [
                "database error", "query failed", "deadlock",
                "sql error", "database connection", "transaction failed",
                "database timeout", "constraint violation"
            ],
            "network_issues": [
                "network error", "unreachable", "dns error",
                "network timeout", "host unreachable", "network unreachable",
                "connection timeout", "network failure"
            ],
            "timeout_issues": [
                "timeout", "timed out", "time out",
                "request timeout", "operation timeout", "timeout error",
                "time limit exceeded", "timeout occurred"
            ],
            "null_reference": [
                "null pointer", "undefined", "null reference",
                "null exception", "null value", "undefined variable",
                "null object", "null pointer exception"
            ]
        }
        
        # Count matches for each category
        category_counts = defaultdict(int)
        category_examples = defaultdict(list)
        
        for entry in log_entries:
            message = entry["message"].lower()
            
            for category, keywords in root_cause_categories.items():
                for keyword in keywords:
                    if keyword in message:
                        category_counts[category] += 1
                        
                        # Store example messages (max 3 per category)
                        if len(category_examples[category]) < 3:
                            category_examples[category].append({
                                "message": entry["message"][:100] + "..." if len(entry["message"]) > 100 else entry["message"],
                                "timestamp": entry["timestamp"].isoformat(),
                                "log_level": entry["log_level"],
                                "source": entry["source"] or "Unknown"
                            })
                        break  # Only count once per message per category
        
        # Create results sorted by count
        potential_root_causes = []
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            if count > 0:
                potential_root_causes.append({
                    "category": category.replace("_", " ").title(),
                    "count": count,
                    "percentage": round((count / len(log_entries)) * 100, 2),
                    "examples": category_examples[category]
                })
        
        return potential_root_causes
    
    def _find_error_correlations(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find correlations between different error types
        Group errors by 5-minute time windows and analyze co-occurrence
        """
        if not log_entries:
            return []
        
        # Group errors by 5-minute time windows
        time_windows = defaultdict(list)
        
        for entry in log_entries:
            # Round to 5-minute window
            timestamp = entry["timestamp"]
            minute = timestamp.minute
            rounded_minute = (minute // 5) * 5
            window_time = timestamp.replace(minute=rounded_minute, second=0, microsecond=0)
            
            time_windows[window_time].append(entry)
        
        # Analyze correlations in each window
        correlations = []
        
        for window_time, entries in time_windows.items():
            if len(entries) < 2:  # Need at least 2 errors for correlation
                continue
            
            # Categorize error types in this window
            error_types = set()
            for entry in entries:
                error_type = self._categorize_error_type(entry["message"])
                error_types.add(error_type)
            
            if len(error_types) > 1:  # Multiple different error types
                unique_types = len(error_types)
                total_errors = len(entries)
                correlation_score = unique_types / total_errors
                
                # Get sample errors from this window
                sample_errors = []
                for entry in entries[:5]:  # Max 5 samples
                    sample_errors.append({
                        "message": entry["message"][:80] + "..." if len(entry["message"]) > 80 else entry["message"],
                        "log_level": entry["log_level"],
                        "error_type": self._categorize_error_type(entry["message"]),
                        "timestamp": entry["timestamp"].isoformat()
                    })
                
                correlations.append({
                    "window_start": window_time.isoformat(),
                    "unique_error_types": unique_types,
                    "total_errors": total_errors,
                    "correlation_score": round(correlation_score, 3),
                    "error_types": list(error_types),
                    "sample_errors": sample_errors
                })
        
        # Return top 10 correlations by score
        return sorted(correlations, key=lambda x: x["correlation_score"], reverse=True)[:10]
    
    def _categorize_error_type(self, message: str) -> str:
        """
        Categorize error message into predefined types
        """
        message_lower = message.lower()
        
        # Define error type keywords
        error_types = {
            "timeout": ["timeout", "timed out", "time out"],
            "connection": ["connection", "connect", "unreachable"],
            "null_reference": ["null", "undefined", "none"],
            "permission": ["permission", "access denied", "forbidden", "unauthorized"],
            "database": ["database", "sql", "query", "deadlock"],
            "network": ["network", "dns", "unreachable", "host"],
            "memory": ["memory", "out of memory", "allocation"],
            "other": []  # Default category
        }
        
        # Check each category
        for error_type, keywords in error_types.items():
            if error_type == "other":
                continue
            for keyword in keywords:
                if keyword in message_lower:
                    return error_type
        
        return "other"
    
    def _cluster_messages(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Simple message clustering by similarity
        Simplify messages and group similar ones
        """
        if not log_entries:
            return []
        
        # Simplify messages for clustering
        simplified_messages = {}
        message_groups = defaultdict(list)
        
        for entry in log_entries:
            message = entry["message"]
            
            # Simplify: remove numbers, special chars, convert to lowercase
            simplified = re.sub(r'\d+', 'N', message.lower())
            simplified = re.sub(r'[^\w\s]', ' ', simplified)
            simplified = re.sub(r'\s+', ' ', simplified).strip()
            
            # Use first 50 characters as cluster key
            cluster_key = simplified[:50]
            
            if cluster_key not in simplified_messages:
                simplified_messages[cluster_key] = simplified
            
            message_groups[cluster_key].append({
                "original_message": message,
                "timestamp": entry["timestamp"].isoformat(),
                "log_level": entry["log_level"],
                "source": entry["source"] or "Unknown"
            })
        
        # Create clusters (only include groups with >1 message)
        clusters = []
        for cluster_key, messages in message_groups.items():
            if len(messages) > 1:  # Only clusters with multiple messages
                # Get sample messages (max 3)
                sample_messages = []
                for msg in messages[:3]:
                    sample_messages.append({
                        "message": msg["original_message"][:100] + "..." if len(msg["original_message"]) > 100 else msg["original_message"],
                        "timestamp": msg["timestamp"],
                        "log_level": msg["log_level"],
                        "source": msg["source"]
                    })
                
                clusters.append({
                    "cluster_key": cluster_key,
                    "simplified_pattern": simplified_messages[cluster_key],
                    "message_count": len(messages),
                    "sample_messages": sample_messages,
                    "frequency_percent": round((len(messages) / len(log_entries)) * 100, 2)
                })
        
        # Return top 15 clusters by message count
        return sorted(clusters, key=lambda x: x["message_count"], reverse=True)[:15]
