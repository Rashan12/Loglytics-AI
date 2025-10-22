import asyncio
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, and_

from app.models.alert import Alert
from app.models.live_log_connection import LiveLogConnection

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    ERROR_RATE = "error_rate"
    PATTERN_MATCH = "pattern_match"
    ANOMALY = "anomaly"
    KEYWORD = "keyword"
    LOG_LEVEL = "log_level"

@dataclass
class AlertRule:
    id: str
    project_id: str
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    enabled: bool
    conditions: Dict[str, Any]
    cooldown_minutes: int
    notification_channels: List[str]
    last_triggered: Optional[datetime] = None

class AlertEngine:
    """
    Alert engine for real-time log monitoring
    Detects patterns, anomalies, and triggers alerts
    """
    
    def __init__(self, db: AsyncSession, redis_client):
        self.db = db
        self.redis = redis_client
        self.alert_rules_cache = {}
        self.rate_counters = {}  # For rate-based alerts
        self.pattern_cache = {}  # For compiled regex patterns
        
    async def get_alert_rules(self, project_id: str) -> List[AlertRule]:
        """Get alert rules for a project"""
        try:
            # Check cache first
            cache_key = f"alert_rules:{project_id}"
            if cache_key in self.alert_rules_cache:
                return self.alert_rules_cache[cache_key]
            
            # Load from database (this would be implemented with a proper alert_rules table)
            # For now, return default rules
            default_rules = self._get_default_rules(project_id)
            
            # Cache the rules
            self.alert_rules_cache[cache_key] = default_rules
            
            return default_rules
            
        except Exception as e:
            logger.error(f"Failed to get alert rules: {str(e)}")
            return []
    
    def _get_default_rules(self, project_id: str) -> List[AlertRule]:
        """Get default alert rules for a project"""
        return [
            AlertRule(
                id="error_rate_high",
                project_id=project_id,
                name="High Error Rate",
                alert_type=AlertType.ERROR_RATE,
                severity=AlertSeverity.HIGH,
                enabled=True,
                conditions={
                    "threshold": 10,  # errors per minute
                    "window_minutes": 5
                },
                cooldown_minutes=15,
                notification_channels=["in_app", "email"]
            ),
            AlertRule(
                id="critical_errors",
                project_id=project_id,
                name="Critical Errors",
                alert_type=AlertType.LOG_LEVEL,
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                conditions={
                    "log_levels": ["CRITICAL", "FATAL"]
                },
                cooldown_minutes=5,
                notification_channels=["in_app", "email", "slack"]
            ),
            AlertRule(
                id="database_errors",
                project_id=project_id,
                name="Database Connection Errors",
                alert_type=AlertType.PATTERN_MATCH,
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                conditions={
                    "pattern": r"(?i)(database|connection|sql).*?(error|failed|timeout)",
                    "case_sensitive": False
                },
                cooldown_minutes=10,
                notification_channels=["in_app"]
            )
        ]
    
    async def check_log(self, log: Dict[str, Any], rules: List[AlertRule]):
        """Check a single log against alert rules"""
        try:
            for rule in rules:
                if not rule.enabled:
                    continue
                
                # Check cooldown
                if self._is_in_cooldown(rule):
                    continue
                
                # Check rule based on type
                if rule.alert_type == AlertType.ERROR_RATE:
                    await self._check_error_rate_alert(log, rule)
                elif rule.alert_type == AlertType.PATTERN_MATCH:
                    await self._check_pattern_alert(log, rule)
                elif rule.alert_type == AlertType.LOG_LEVEL:
                    await self._check_log_level_alert(log, rule)
                elif rule.alert_type == AlertType.KEYWORD:
                    await self._check_keyword_alert(log, rule)
                elif rule.alert_type == AlertType.ANOMALY:
                    await self._check_anomaly_alert(log, rule)
                    
        except Exception as e:
            logger.error(f"Failed to check log against rules: {str(e)}")
    
    async def _check_error_rate_alert(self, log: Dict[str, Any], rule: AlertRule):
        """Check error rate alert"""
        try:
            if log["log_level"] not in ["ERROR", "CRITICAL"]:
                return
            
            project_id = log["project_id"]
            threshold = rule.conditions["threshold"]
            window_minutes = rule.conditions["window_minutes"]
            
            # Update rate counter
            current_time = datetime.utcnow()
            window_start = current_time - timedelta(minutes=window_minutes)
            
            # Get error count for the window
            error_count = await self._get_error_count(project_id, window_start, current_time)
            
            if error_count >= threshold:
                await self._trigger_alert(rule, {
                    "error_count": error_count,
                    "threshold": threshold,
                    "window_minutes": window_minutes,
                    "log": log
                })
                
        except Exception as e:
            logger.error(f"Failed to check error rate alert: {str(e)}")
    
    async def _check_pattern_alert(self, log: Dict[str, Any], rule: AlertRule):
        """Check pattern match alert"""
        try:
            pattern = rule.conditions["pattern"]
            case_sensitive = rule.conditions.get("case_sensitive", True)
            
            # Compile pattern if not cached
            cache_key = f"pattern:{pattern}:{case_sensitive}"
            if cache_key not in self.pattern_cache:
                flags = 0 if case_sensitive else re.IGNORECASE
                self.pattern_cache[cache_key] = re.compile(pattern, flags)
            
            compiled_pattern = self.pattern_cache[cache_key]
            
            # Check message and raw content
            text_to_check = f"{log['message']} {log.get('raw_content', '')}"
            
            if compiled_pattern.search(text_to_check):
                await self._trigger_alert(rule, {
                    "matched_text": compiled_pattern.search(text_to_check).group(),
                    "pattern": pattern,
                    "log": log
                })
                
        except Exception as e:
            logger.error(f"Failed to check pattern alert: {str(e)}")
    
    async def _check_log_level_alert(self, log: Dict[str, Any], rule: AlertRule):
        """Check log level alert"""
        try:
            target_levels = rule.conditions["log_levels"]
            
            if log["log_level"] in target_levels:
                await self._trigger_alert(rule, {
                    "log_level": log["log_level"],
                    "target_levels": target_levels,
                    "log": log
                })
                
        except Exception as e:
            logger.error(f"Failed to check log level alert: {str(e)}")
    
    async def _check_keyword_alert(self, log: Dict[str, Any], rule: AlertRule):
        """Check keyword alert"""
        try:
            keywords = rule.conditions["keywords"]
            case_sensitive = rule.conditions.get("case_sensitive", False)
            
            text_to_check = f"{log['message']} {log.get('raw_content', '')}"
            if not case_sensitive:
                text_to_check = text_to_check.lower()
                keywords = [kw.lower() for kw in keywords]
            
            matched_keywords = [kw for kw in keywords if kw in text_to_check]
            
            if matched_keywords:
                await self._trigger_alert(rule, {
                    "matched_keywords": matched_keywords,
                    "keywords": keywords,
                    "log": log
                })
                
        except Exception as e:
            logger.error(f"Failed to check keyword alert: {str(e)}")
    
    async def _check_anomaly_alert(self, log: Dict[str, Any], rule: AlertRule):
        """Check anomaly alert (placeholder for future ML-based detection)"""
        try:
            # This would integrate with the anomaly detection service
            # For now, just log that anomaly checking is not implemented
            logger.debug("Anomaly alert checking not yet implemented")
            
        except Exception as e:
            logger.error(f"Failed to check anomaly alert: {str(e)}")
    
    async def _trigger_alert(self, rule: AlertRule, context: Dict[str, Any]):
        """Trigger an alert"""
        try:
            # Create alert record
            alert_data = {
                "id": self._generate_uuid(),
                "user_id": context["log"]["user_id"],
                "project_id": rule.project_id,
                "live_connection_id": context["log"].get("live_connection_id"),
                "alert_type": rule.alert_type.value,
                "severity": rule.severity.value,
                "message": self._generate_alert_message(rule, context),
                "metadata": {
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "context": context,
                    "triggered_at": datetime.utcnow().isoformat()
                },
                "is_read": False,
                "notified_via": [],
                "created_at": datetime.utcnow()
            }
            
            # Store alert in database
            await self.db.execute(insert(Alert), alert_data)
            await self.db.commit()
            
            # Update rule last triggered time
            rule.last_triggered = datetime.utcnow()
            
            # Send notifications
            await self._send_notifications(rule, alert_data)
            
            logger.info(f"Alert triggered: {rule.name} for project {rule.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {str(e)}")
    
    def _generate_alert_message(self, rule: AlertRule, context: Dict[str, Any]) -> str:
        """Generate alert message based on rule and context"""
        if rule.alert_type == AlertType.ERROR_RATE:
            return f"High error rate detected: {context['error_count']} errors in {context['window_minutes']} minutes (threshold: {context['threshold']})"
        
        elif rule.alert_type == AlertType.PATTERN_MATCH:
            return f"Pattern match detected: '{context['matched_text']}' in log message"
        
        elif rule.alert_type == AlertType.LOG_LEVEL:
            return f"Critical log level detected: {context['log_level']}"
        
        elif rule.alert_type == AlertType.KEYWORD:
            return f"Keyword match detected: {', '.join(context['matched_keywords'])}"
        
        else:
            return f"Alert triggered: {rule.name}"
    
    async def _send_notifications(self, rule: AlertRule, alert_data: Dict[str, Any]):
        """Send notifications via configured channels"""
        try:
            channels = rule.notification_channels
            
            for channel in channels:
                if channel == "in_app":
                    # Already stored in database
                    pass
                elif channel == "email":
                    await self._send_email_notification(rule, alert_data)
                elif channel == "slack":
                    await self._send_slack_notification(rule, alert_data)
                elif channel == "jira":
                    await self._create_jira_ticket(rule, alert_data)
                    
        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}")
    
    async def _send_email_notification(self, rule: AlertRule, alert_data: Dict[str, Any]):
        """Send email notification (placeholder)"""
        # This would integrate with SendGrid, SES, etc.
        logger.info(f"Email notification sent for alert {alert_data['id']}")
    
    async def _send_slack_notification(self, rule: AlertRule, alert_data: Dict[str, Any]):
        """Send Slack notification (placeholder)"""
        # This would integrate with Slack webhook
        logger.info(f"Slack notification sent for alert {alert_data['id']}")
    
    async def _create_jira_ticket(self, rule: AlertRule, alert_data: Dict[str, Any]):
        """Create Jira ticket (placeholder)"""
        # This would integrate with Jira API
        logger.info(f"Jira ticket created for alert {alert_data['id']}")
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Check if rule is in cooldown period"""
        if not rule.last_triggered:
            return False
        
        cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
        return datetime.utcnow() < cooldown_end
    
    async def _get_error_count(self, project_id: str, start_time: datetime, end_time: datetime) -> int:
        """Get error count for a time window"""
        try:
            query = select(LogEntry).filter(
                and_(
                    LogEntry.project_id == project_id,
                    LogEntry.log_level.in_(["ERROR", "CRITICAL"]),
                    LogEntry.timestamp >= start_time,
                    LogEntry.timestamp <= end_time
                )
            )
            result = await self.db.execute(query)
            logs = result.scalars().all()
            return len(logs)
            
        except Exception as e:
            logger.error(f"Failed to get error count: {str(e)}")
            return 0
    
    def _generate_uuid(self) -> str:
        """Generate a UUID string"""
        import uuid
        return str(uuid.uuid4())
    
    async def get_active_alerts(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get active alerts for a project"""
        try:
            query = select(Alert).filter(
                and_(
                    Alert.project_id == project_id,
                    Alert.is_read == False
                )
            ).order_by(Alert.created_at.desc()).limit(limit)
            
            result = await self.db.execute(query)
            alerts = result.scalars().all()
            
            return [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "metadata": alert.metadata,
                    "created_at": alert.created_at.isoformat(),
                    "is_read": alert.is_read
                }
                for alert in alerts
            ]
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {str(e)}")
            return []
    
    async def mark_alert_read(self, alert_id: str, user_id: str) -> bool:
        """Mark an alert as read"""
        try:
            from sqlalchemy import update
            
            query = update(Alert).where(
                and_(
                    Alert.id == alert_id,
                    Alert.user_id == user_id
                )
            ).values(is_read=True)
            
            result = await self.db.execute(query)
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to mark alert as read: {str(e)}")
            return False
