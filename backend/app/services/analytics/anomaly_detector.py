from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.models import LogEntry, LogLevel
import numpy as np
from collections import defaultdict

class AnomalyDetector:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def detect_anomalies(
        self,
        project_id: str,
        log_file_id: Optional[str] = None,
        threshold: float = 2.0
    ) -> Dict[str, Any]:
        """
        Main method to detect all types of anomalies
        Returns comprehensive anomaly report
        """
        # Get log entries for analysis
        log_entries = await self._get_log_entries(project_id, log_file_id)
        
        if not log_entries:
            return {
                "total_entries_analyzed": 0,
                "threshold": threshold,
                "statistical_anomalies": [],
                "volume_anomalies": [],
                "temporal_anomalies": [],
                "pattern_anomalies": [],
                "anomaly_scores": [],
                "summary": {
                    "total_anomalies": 0,
                    "high_risk_count": 0,
                    "medium_risk_count": 0,
                    "low_risk_count": 0
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Detect different types of anomalies
        statistical_anomalies = self._detect_statistical_anomalies(log_entries, threshold)
        volume_anomalies = self._detect_volume_anomalies(log_entries, threshold)
        temporal_anomalies = self._detect_temporal_anomalies(log_entries)
        pattern_anomalies = self._detect_pattern_anomalies(log_entries)
        
        # Calculate anomaly scores
        anomaly_scores = self._calculate_anomaly_scores(
            log_entries, statistical_anomalies, volume_anomalies
        )
        
        # Calculate summary statistics
        summary = self._calculate_summary(
            statistical_anomalies, volume_anomalies, temporal_anomalies, pattern_anomalies
        )
        
        return {
            "total_entries_analyzed": len(log_entries),
            "threshold": threshold,
            "statistical_anomalies": statistical_anomalies,
            "volume_anomalies": volume_anomalies,
            "temporal_anomalies": temporal_anomalies,
            "pattern_anomalies": pattern_anomalies,
            "anomaly_scores": anomaly_scores,
            "summary": summary,
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
            LogEntry.source
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
                "source": row.source
            }
            for row in rows
        ]
    
    def _detect_statistical_anomalies(
        self,
        log_entries: List[Dict[str, Any]],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Detect statistical anomalies using Z-score method
        Groups logs by hour and finds entries with |z-score| > threshold
        """
        if len(log_entries) < 10:  # Need minimum data points
            return []
        
        # Group logs by hour
        hourly_counts = defaultdict(int)
        for entry in log_entries:
            hour_key = entry["timestamp"].replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        if len(hourly_counts) < 3:  # Need variation for z-score
            return []
        
        # Convert to arrays for numpy calculations
        hours = list(hourly_counts.keys())
        counts = list(hourly_counts.values())
        
        # Calculate z-scores
        mean_count = np.mean(counts)
        std_count = np.std(counts)
        
        if std_count == 0:  # No variation
            return []
        
        z_scores = [(count - mean_count) / std_count for count in counts]
        
        # Find anomalies
        anomalies = []
        for i, (hour, count, z_score) in enumerate(zip(hours, counts, z_scores)):
            if abs(z_score) > threshold:
                anomalies.append({
                    "timestamp": hour.isoformat(),
                    "log_count": count,
                    "z_score": round(z_score, 3),
                    "severity": "high" if abs(z_score) > 3 else "medium",
                    "type": "spike" if z_score > 0 else "drop"
                })
        
        # Return top 10 anomalies by absolute z-score
        return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)[:10]
    
    def _detect_volume_anomalies(
        self,
        log_entries: List[Dict[str, Any]],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Detect volume anomalies (sudden spikes or drops)
        Compare consecutive time windows for >100% change
        """
        if len(log_entries) < 20:  # Need minimum data for comparison
            return []
        
        # Group logs by hour
        hourly_counts = defaultdict(int)
        for entry in log_entries:
            hour_key = entry["timestamp"].replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        # Sort by time
        sorted_hours = sorted(hourly_counts.keys())
        
        anomalies = []
        for i in range(1, len(sorted_hours)):
            prev_hour = sorted_hours[i-1]
            curr_hour = sorted_hours[i]
            prev_count = hourly_counts[prev_hour]
            curr_count = hourly_counts[curr_hour]
            
            if prev_count == 0:  # Avoid division by zero
                continue
            
            # Calculate percentage change
            change_percent = ((curr_count - prev_count) / prev_count) * 100
            
            # Detect significant changes
            if abs(change_percent) > 100:  # >100% change
                anomaly_type = "spike" if change_percent > 0 else "drop"
                severity = "high" if abs(change_percent) > 200 else "medium"
                
                anomalies.append({
                    "timestamp": curr_hour.isoformat(),
                    "previous_hour": prev_hour.isoformat(),
                    "current_count": curr_count,
                    "previous_count": prev_count,
                    "change_percent": round(change_percent, 2),
                    "type": anomaly_type,
                    "severity": severity
                })
        
        # Return top 10 volume anomalies by change percentage
        return sorted(anomalies, key=lambda x: abs(x["change_percent"]), reverse=True)[:10]
    
    def _detect_temporal_anomalies(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect temporal anomalies (errors at unusual times)
        Find hours with 3x expected error distribution
        """
        if len(log_entries) < 50:  # Need sufficient data
            return []
        
        # Count errors by hour of day
        hourly_errors = defaultdict(int)
        total_errors = 0
        
        for entry in log_entries:
            if entry["log_level"] in ["ERROR", "CRITICAL"]:
                hour = entry["timestamp"].hour
                hourly_errors[hour] += 1
                total_errors += 1
        
        if total_errors < 10:  # Need minimum errors
            return []
        
        # Calculate expected uniform distribution
        expected_per_hour = total_errors / 24
        threshold = expected_per_hour * 3  # 3x expected
        
        anomalies = []
        for hour in range(24):
            error_count = hourly_errors[hour]
            if error_count > threshold:
                ratio = error_count / expected_per_hour if expected_per_hour > 0 else 0
                anomalies.append({
                    "hour": hour,
                    "error_count": error_count,
                    "expected_count": round(expected_per_hour, 2),
                    "ratio": round(ratio, 2),
                    "severity": "high" if ratio > 5 else "medium"
                })
        
        # Return sorted by error count
        return sorted(anomalies, key=lambda x: x["error_count"], reverse=True)
    
    def _detect_pattern_anomalies(
        self,
        log_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect pattern anomalies (rare error messages)
        Find error messages appearing <5% of time
        """
        if len(log_entries) < 20:  # Need minimum data
            return []
        
        # Count error messages
        error_messages = defaultdict(int)
        total_errors = 0
        
        for entry in log_entries:
            if entry["log_level"] in ["ERROR", "CRITICAL"]:
                error_messages[entry["message"]] += 1
                total_errors += 1
        
        if total_errors < 10:  # Need minimum errors
            return []
        
        # Find rare errors (<5% of total)
        threshold = total_errors * 0.05
        rare_errors = []
        
        for message, count in error_messages.items():
            if count < threshold and count > 0:
                percentage = (count / total_errors) * 100
                rare_errors.append({
                    "message": message[:100] + "..." if len(message) > 100 else message,
                    "count": count,
                    "percentage": round(percentage, 2),
                    "severity": "high" if count == 1 else "medium"
                })
        
        # Return top 10 rare errors by rarity
        return sorted(rare_errors, key=lambda x: x["percentage"])[:10]
    
    def _calculate_anomaly_scores(
        self,
        log_entries: List[Dict[str, Any]],
        statistical_anomalies: List[Dict[str, Any]],
        volume_anomalies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate anomaly scores (0-1) for each time period
        Combines multiple anomaly signals with weighted scoring
        """
        if not log_entries:
            return []
        
        # Group logs by hour for scoring
        hourly_data = defaultdict(lambda: {
            "total_logs": 0,
            "errors": 0,
            "sources": set(),
            "timestamp": None
        })
        
        for entry in log_entries:
            hour_key = entry["timestamp"].replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key]["total_logs"] += 1
            hourly_data[hour_key]["timestamp"] = hour_key
            
            if entry["log_level"] in ["ERROR", "CRITICAL"]:
                hourly_data[hour_key]["errors"] += 1
            
            if entry["source"]:
                hourly_data[hour_key]["sources"].add(entry["source"])
        
        # Calculate scores for each hour
        scores = []
        for hour_key, data in hourly_data.items():
            score = 0.0
            
            # Anomalous time factor (0.5 weight)
            hour = hour_key.hour
            if 2 <= hour <= 6:  # Night hours are more anomalous
                score += 0.5
            
            # High error rate factor (0.3 weight)
            error_rate = data["errors"] / data["total_logs"] if data["total_logs"] > 0 else 0
            if error_rate > 0.1:  # >10% error rate
                score += 0.3 * min(error_rate * 10, 1.0)  # Scale to 0-1
            
            # High volume factor (0.2 weight)
            # Use percentile-based scoring
            all_counts = [d["total_logs"] for d in hourly_data.values()]
            if all_counts:
                percentile_90 = np.percentile(all_counts, 90)
                if data["total_logs"] > percentile_90:
                    score += 0.2
            
            # Check if this hour has statistical anomalies
            for stat_anomaly in statistical_anomalies:
                if stat_anomaly["timestamp"] == hour_key.isoformat():
                    score += 0.2  # Bonus for statistical anomaly
            
            # Check if this hour has volume anomalies
            for vol_anomaly in volume_anomalies:
                if vol_anomaly["timestamp"] == hour_key.isoformat():
                    score += 0.1  # Bonus for volume anomaly
            
            # Cap score at 1.0
            score = min(score, 1.0)
            
            if score > 0.1:  # Only include significant scores
                scores.append({
                    "timestamp": hour_key.isoformat(),
                    "score": round(score, 3),
                    "total_logs": data["total_logs"],
                    "errors": data["errors"],
                    "error_rate": round(error_rate, 3),
                    "unique_sources": len(data["sources"]),
                    "severity": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
                })
        
        # Return top 20 scored time periods
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:20]
    
    def _calculate_summary(
        self,
        statistical_anomalies: List[Dict[str, Any]],
        volume_anomalies: List[Dict[str, Any]],
        temporal_anomalies: List[Dict[str, Any]],
        pattern_anomalies: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate summary statistics for all anomaly types"""
        total_anomalies = (
            len(statistical_anomalies) + 
            len(volume_anomalies) + 
            len(temporal_anomalies) + 
            len(pattern_anomalies)
        )
        
        # Count by severity
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        for anomaly_list in [statistical_anomalies, volume_anomalies, temporal_anomalies, pattern_anomalies]:
            for anomaly in anomaly_list:
                severity = anomaly.get("severity", "low")
                if severity == "high":
                    high_risk += 1
                elif severity == "medium":
                    medium_risk += 1
                else:
                    low_risk += 1
        
        return {
            "total_anomalies": total_anomalies,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk
        }
