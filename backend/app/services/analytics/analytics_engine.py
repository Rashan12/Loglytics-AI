from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import json
from app.models import LogEntry, LogFile, AnalyticsCache
from app.services.analytics.metrics_calculator import MetricsCalculator
from app.services.analytics.anomaly_detector import AnomalyDetector
from app.services.analytics.performance_analyzer import PerformanceAnalyzer
from app.services.analytics.pattern_analyzer import PatternAnalyzer
from app.database import get_db

class AnalyticsEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_calculator = MetricsCalculator(db)
        self.anomaly_detector = AnomalyDetector(db)
        self.performance_analyzer = PerformanceAnalyzer(db)
        self.pattern_analyzer = PatternAnalyzer(db)
    
    async def get_or_compute_analytics(
        self,
        project_id: str,
        analytics_type: str,
        log_file_id: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get analytics from cache or compute if not cached
        """
        # Check cache first
        if not force_refresh:
            cached = await self._get_from_cache(project_id, analytics_type, log_file_id)
            if cached:
                return cached
        
        # Compute analytics based on type
        if analytics_type == "overview":
            result = await self.compute_overview(project_id, log_file_id)
        elif analytics_type == "errors":
            result = await self.compute_error_analysis(project_id, log_file_id)
        elif analytics_type == "anomalies":
            result = await self.compute_anomaly_detection(project_id, log_file_id)
        elif analytics_type == "performance":
            result = await self.compute_performance_metrics(project_id, log_file_id)
        elif analytics_type == "patterns":
            result = await self.compute_pattern_analysis(project_id, log_file_id)
        elif analytics_type == "insights":
            result = await self.generate_insights(project_id, log_file_id)
        else:
            raise ValueError(f"Unknown analytics type: {analytics_type}")
        
        # Cache the result
        await self._save_to_cache(project_id, analytics_type, log_file_id, result)
        
        return result
    
    async def _get_from_cache(
        self,
        project_id: str,
        analytics_type: str,
        log_file_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get analytics from cache"""
        query = select(AnalyticsCache).filter(
            AnalyticsCache.project_id == project_id,
            AnalyticsCache.analytics_type == analytics_type
        )
        
        if log_file_id:
            query = query.filter(AnalyticsCache.log_file_id == log_file_id)
        
        # Check if cache is not older than 1 hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        query = query.filter(AnalyticsCache.updated_at >= one_hour_ago)
        
        result = await self.db.execute(query)
        cache_entry = result.scalar_one_or_none()
        
        if cache_entry:
            return cache_entry.analytics_data
        
        return None
    
    async def _save_to_cache(
        self,
        project_id: str,
        analytics_type: str,
        log_file_id: Optional[str],
        data: Dict[str, Any]
    ):
        """Save analytics to cache"""
        # Check if entry exists
        query = select(AnalyticsCache).filter(
            AnalyticsCache.project_id == project_id,
            AnalyticsCache.analytics_type == analytics_type
        )
        
        if log_file_id:
            query = query.filter(AnalyticsCache.log_file_id == log_file_id)
        
        result = await self.db.execute(query)
        cache_entry = result.scalar_one_or_none()
        
        if cache_entry:
            # Update existing
            cache_entry.analytics_data = data
            cache_entry.updated_at = datetime.utcnow()
        else:
            # Create new
            cache_entry = AnalyticsCache(
                project_id=project_id,
                analytics_type=analytics_type,
                log_file_id=log_file_id,
                analytics_data=data
            )
            self.db.add(cache_entry)
        
        await self.db.commit()
    
    async def compute_overview(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute overview analytics - to be implemented"""
        return await self.metrics_calculator.calculate_overview(project_id, log_file_id)
    
    async def compute_error_analysis(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute error analysis - to be implemented"""
        return await self.metrics_calculator.calculate_error_analysis(project_id, log_file_id)
    
    async def compute_anomaly_detection(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute anomaly detection - to be implemented"""
        return await self.anomaly_detector.detect_anomalies(project_id, log_file_id)
    
    async def compute_performance_metrics(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute performance metrics - to be implemented"""
        return await self.performance_analyzer.analyze_performance(project_id, log_file_id)
    
    async def compute_pattern_analysis(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute pattern analysis - to be implemented"""
        return await self.pattern_analyzer.analyze_patterns(project_id, log_file_id)
    
    async def generate_insights(
        self,
        project_id: str,
        log_file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights by combining all analytics
        Provides actionable recommendations and health scoring
        """
        # Gather all analytics data
        overview = await self.metrics_calculator.calculate_overview(project_id, log_file_id)
        errors = await self.metrics_calculator.calculate_error_analysis(project_id, log_file_id)
        anomalies = await self.anomaly_detector.detect_anomalies(project_id, log_file_id)
        patterns = await self.pattern_analyzer.analyze_patterns(project_id, log_file_id)
        performance = await self.performance_analyzer.analyze_performance(project_id, log_file_id)
        
        insights = []
        recommendations = []
        
        # A. ERROR RATE ANALYSIS
        total_logs = overview.get("total_count", 0)
        error_count = sum(level["value"] for level in overview.get("log_level_distribution", []) 
                         if level["name"] in ["ERROR", "CRITICAL"])
        
        if total_logs > 0:
            error_rate = (error_count / total_logs) * 100
            
            if error_rate > 10:
                insights.append({
                    "type": "error_rate",
                    "severity": "high",
                    "message": f"Error rate is {error_rate:.1f}%, above 10% threshold",
                    "impact": "High error rate indicates system instability"
                })
                recommendations.append({
                    "action": "Investigate top error sources and implement fixes",
                    "priority": "high",
                    "estimated_impact": "Reduce error rate by 50-70%"
                })
            elif error_rate > 5:
                insights.append({
                    "type": "error_rate",
                    "severity": "medium",
                    "message": f"Error rate is {error_rate:.1f}%, slightly elevated",
                    "impact": "Moderate error rate suggests some issues need attention"
                })
                recommendations.append({
                    "action": "Review and address most frequent errors",
                    "priority": "medium",
                    "estimated_impact": "Improve system reliability by 30-40%"
                })
            else:
                insights.append({
                    "type": "error_rate",
                    "severity": "info",
                    "message": f"Error rate is {error_rate:.1f}%, within acceptable range",
                    "impact": "System error rate is healthy"
                })
        
        # B. MTBF ANALYSIS
        mtbf_hours = errors.get("mtbf_hours", 0)
        if mtbf_hours > 0:
            if mtbf_hours < 1:
                insights.append({
                    "type": "mtbf",
                    "severity": "critical",
                    "message": f"MTBF is only {mtbf_hours:.1f} hours - system failing frequently",
                    "impact": "Frequent failures indicate critical system issues"
                })
                recommendations.append({
                    "action": "Implement immediate error prevention and monitoring",
                    "priority": "critical",
                    "estimated_impact": "Increase system stability by 80-90%"
                })
            elif mtbf_hours < 24:
                insights.append({
                    "type": "mtbf",
                    "severity": "medium",
                    "message": f"MTBF is {mtbf_hours:.1f} hours - some reliability concerns",
                    "impact": "System has moderate reliability issues"
                })
                recommendations.append({
                    "action": "Improve error handling and system resilience",
                    "priority": "medium",
                    "estimated_impact": "Extend MTBF by 2-3x"
                })
            else:
                insights.append({
                    "type": "mtbf",
                    "severity": "info",
                    "message": f"MTBF is {mtbf_hours:.1f} hours - system is stable",
                    "impact": "System demonstrates good reliability"
                })
        
        # C. ANOMALY DETECTION
        anomaly_summary = anomalies.get("summary", {})
        high_risk_count = anomaly_summary.get("high_risk_count", 0)
        
        if high_risk_count > 5:
            insights.append({
                "type": "anomalies",
                "severity": "high",
                "message": f"Detected {high_risk_count} high-risk anomalies",
                "impact": "Multiple anomalies suggest system instability"
            })
            recommendations.append({
                "action": "Review anomalous time periods and investigate root causes",
                "priority": "high",
                "estimated_impact": "Prevent potential system failures"
            })
        elif high_risk_count > 0:
            insights.append({
                "type": "anomalies",
                "severity": "medium",
                "message": f"Detected {high_risk_count} high-risk anomalies",
                "impact": "Some anomalies detected that need attention"
            })
            recommendations.append({
                "action": "Monitor anomalous patterns and address underlying issues",
                "priority": "medium",
                "estimated_impact": "Improve system predictability"
            })
        
        # D. PERFORMANCE ISSUES
        slow_operations = performance.get("slow_operations", [])
        if len(slow_operations) > 10:
            insights.append({
                "type": "performance",
                "severity": "medium",
                "message": f"Detected {len(slow_operations)} slow operations",
                "impact": "Multiple slow operations affecting user experience"
            })
            recommendations.append({
                "action": "Optimize slow queries and database operations",
                "priority": "medium",
                "estimated_impact": "Improve response times by 30-50%"
            })
        elif len(slow_operations) > 0:
            insights.append({
                "type": "performance",
                "severity": "info",
                "message": f"Detected {len(slow_operations)} slow operations",
                "impact": "Some performance optimizations available"
            })
            recommendations.append({
                "action": "Review and optimize identified slow operations",
                "priority": "low",
                "estimated_impact": "Moderate performance improvement"
            })
        
        # E. PATTERN ANALYSIS
        root_causes = patterns.get("potential_root_causes", [])
        if root_causes:
            top_cause = root_causes[0]
            insights.append({
                "type": "root_cause",
                "severity": "high" if top_cause["percentage"] > 20 else "medium",
                "message": f"Primary issue: {top_cause['category']}, accounts for {top_cause['percentage']:.1f}% of errors",
                "impact": f"Focusing on this issue could resolve {top_cause['percentage']:.1f}% of problems"
            })
            recommendations.append({
                "action": f"Focus on resolving {top_cause['category'].lower()} issues",
                "priority": "high" if top_cause["percentage"] > 20 else "medium",
                "estimated_impact": f"Reduce errors by {top_cause['percentage']:.1f}%"
            })
        
        # F. TEMPORAL PATTERNS
        temporal_anomalies = anomalies.get("temporal_anomalies", [])
        if temporal_anomalies:
            unusual_hours = [anomaly["hour"] for anomaly in temporal_anomalies[:5]]
            insights.append({
                "type": "temporal",
                "severity": "medium",
                "message": f"Errors spike during hours: {', '.join(map(str, unusual_hours))}",
                "impact": "Scheduled jobs or maintenance may be causing issues"
            })
            recommendations.append({
                "action": "Review scheduled jobs and maintenance windows during these hours",
                "priority": "medium",
                "estimated_impact": "Reduce error spikes by 60-80%"
            })
        
        # G. ERROR HOTSPOTS
        error_hotspots = errors.get("error_hotspots", [])
        if error_hotspots:
            top_hotspot = error_hotspots[0]
            insights.append({
                "type": "hotspot",
                "severity": "high" if top_hotspot["error_count"] > 50 else "medium",
                "message": f"Source '{top_hotspot['source']}' has {top_hotspot['error_count']} errors",
                "impact": "This component is the primary source of system errors"
            })
            recommendations.append({
                "action": f"Refactor '{top_hotspot['source']}' component to improve reliability",
                "priority": "high" if top_hotspot["error_count"] > 50 else "medium",
                "estimated_impact": "Reduce component errors by 70-90%"
            })
        
        # Calculate health score
        health_score = self._calculate_health_score(insights)
        
        # Count issues by severity
        critical_issues = sum(1 for insight in insights if insight["severity"] == "critical")
        high_priority_actions = sum(1 for rec in recommendations if rec["priority"] in ["critical", "high"])
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "summary": {
                "total_insights": len(insights),
                "critical_issues": critical_issues,
                "high_priority_actions": high_priority_actions,
                "health_score": health_score
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_health_score(self, insights: List[Dict[str, Any]]) -> int:
        """
        Calculate system health score based on insights severity
        Base score: 100, penalties: critical(-25), high(-15), medium(-10), info(0)
        """
        base_score = 100
        
        for insight in insights:
            severity = insight.get("severity", "info")
            if severity == "critical":
                base_score -= 25
            elif severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 10
            # info severity doesn't reduce score
        
        return max(0, base_score)
    
    async def invalidate_cache(self, project_id: str):
        """Invalidate all cache for a project"""
        await self.db.execute(
            "DELETE FROM analytics_cache WHERE project_id = :project_id",
            {"project_id": project_id}
        )
        await self.db.commit()
