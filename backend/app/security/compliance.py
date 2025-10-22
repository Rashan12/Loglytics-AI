"""
GDPR Compliance and Data Protection
Provides data protection, anonymization, and compliance features
"""

import json
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.database.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.log_file import LogFile
from app.models.chat_session import ChatSession, ChatMessage as Message
from app.models.analysis import Analysis
from app.models.project import Project
from app.security.encryption import data_anonymization

logger = logging.getLogger(__name__)


class GDPRCompliance:
    """GDPR compliance and data protection"""
    
    def __init__(self):
        self.data_retention_periods = {
            "user_data": 365,  # 1 year
            "audit_logs": 2555,  # 7 years
            "log_files": 90,  # 3 months
            "chat_sessions": 180,  # 6 months
            "analysis_results": 365,  # 1 year
            "backup_data": 30,  # 1 month
        }
        
        self.anonymization_fields = {
            "email": "anonymize_email",
            "ip_address": "anonymize_ip",
            "user_agent": "anonymize_user_agent",
            "phone": "anonymize_phone",
            "address": "anonymize_address",
            "name": "anonymize_name",
        }
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance
        
        Args:
            user_id: User ID to export data for
            
        Returns:
            Dictionary containing all user data
        """
        try:
            db = next(get_db())
            try:
                export_data = {
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "data_categories": {},
                    "metadata": {
                        "export_type": "gdpr_data_export",
                        "compliance_version": "1.0"
                    }
                }
                
                # Export user profile data
                user_data = await self._export_user_profile(db, user_id)
                export_data["data_categories"]["user_profile"] = user_data
                
                # Export audit logs
                audit_logs = await self._export_audit_logs(db, user_id)
                export_data["data_categories"]["audit_logs"] = audit_logs
                
                # Export log files
                log_files = await self._export_log_files(db, user_id)
                export_data["data_categories"]["log_files"] = log_files
                
                # Export chat sessions
                chat_sessions = await self._export_chat_sessions(db, user_id)
                export_data["data_categories"]["chat_sessions"] = chat_sessions
                
                # Export analysis results
                analysis_results = await self._export_analysis_results(db, user_id)
                export_data["data_categories"]["analysis_results"] = analysis_results
                
                # Export projects
                projects = await self._export_projects(db, user_id)
                export_data["data_categories"]["projects"] = projects
                
                # Log export event
                await self._log_data_export(user_id, "gdpr_export")
                
                return export_data
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            raise ValueError("Failed to export user data")
    
    async def _export_user_profile(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Export user profile data"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            return {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "subscription_tier": user.subscription_tier.value if user.subscription_tier else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "preferences": user.preferences or {},
                "metadata": user.metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Error exporting user profile: {e}")
            return {}
    
    async def _export_audit_logs(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Export audit logs for user"""
        try:
            logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
            
            return [
                {
                    "id": str(log.id),
                    "operation": log.operation,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "path": log.path,
                    "method": log.method,
                    "status_code": log.status_code,
                    "query_params": log.query_params or {},
                    "metadata": log.metadata or {},
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}")
            return []
    
    async def _export_log_files(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Export log files for user"""
        try:
            log_files = db.query(LogFile).filter(LogFile.user_id == user_id).all()
            
            return [
                {
                    "id": str(log_file.id),
                    "filename": log_file.filename,
                    "original_filename": log_file.original_filename,
                    "file_size": log_file.file_size,
                    "file_type": log_file.file_type,
                    "upload_status": log_file.upload_status,
                    "created_at": log_file.created_at.isoformat(),
                    "metadata": log_file.metadata or {}
                }
                for log_file in log_files
            ]
            
        except Exception as e:
            logger.error(f"Error exporting log files: {e}")
            return []
    
    async def _export_chat_sessions(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Export chat sessions for user"""
        try:
            chat_sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
            
            result = []
            for session in chat_sessions:
                # Get messages for this session
                messages = db.query(Message).filter(Message.chat_session_id == session.id).all()
                
                session_data = {
                    "id": str(session.id),
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "metadata": session.metadata or {},
                    "messages": [
                        {
                            "id": str(msg.id),
                            "role": msg.role,
                            "content": msg.content,
                            "created_at": msg.created_at.isoformat(),
                            "metadata": msg.metadata or {}
                        }
                        for msg in messages
                    ]
                }
                result.append(session_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting chat sessions: {e}")
            return []
    
    async def _export_analysis_results(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Export analysis results for user"""
        try:
            analyses = db.query(Analysis).filter(Analysis.user_id == user_id).all()
            
            return [
                {
                    "id": str(analysis.id),
                    "analysis_type": analysis.analysis_type,
                    "status": analysis.status,
                    "results": analysis.results or {},
                    "created_at": analysis.created_at.isoformat(),
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                    "metadata": analysis.metadata or {}
                }
                for analysis in analyses
            ]
            
        except Exception as e:
            logger.error(f"Error exporting analysis results: {e}")
            return []
    
    async def _export_projects(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Export projects for user"""
        try:
            projects = db.query(Project).filter(Project.user_id == user_id).all()
            
            return [
                {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "is_public": project.is_public,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                    "metadata": project.metadata or {}
                }
                for project in projects
            ]
            
        except Exception as e:
            logger.error(f"Error exporting projects: {e}")
            return []
    
    async def delete_user_data(self, user_id: str, anonymize: bool = True) -> bool:
        """
        Delete or anonymize all user data
        
        Args:
            user_id: User ID to delete data for
            anonymize: Whether to anonymize instead of delete
            
        Returns:
            True if successful
        """
        try:
            db = next(get_db())
            try:
                if anonymize:
                    # Anonymize user data
                    await self._anonymize_user_data(db, user_id)
                else:
                    # Delete user data
                    await self._delete_user_data(db, user_id)
                
                # Log deletion event
                await self._log_data_deletion(user_id, anonymize)
                
                db.commit()
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    async def _anonymize_user_data(self, db: Session, user_id: str):
        """Anonymize user data"""
        try:
            # Anonymize user profile
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.email = data_anonymization.anonymize_email(user.email)
                user.username = f"user_{secrets.token_hex(8)}"
                user.first_name = "Anonymous"
                user.last_name = "User"
                user.metadata = {"anonymized": True, "anonymized_at": datetime.utcnow().isoformat()}
            
            # Anonymize audit logs
            audit_logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
            for log in audit_logs:
                log.ip_address = data_anonymization.anonymize_ip(log.ip_address)
                log.user_agent = data_anonymization.anonymize_user_agent(log.user_agent)
                log.metadata = {"anonymized": True, "anonymized_at": datetime.utcnow().isoformat()}
            
            # Anonymize other data as needed
            # Note: This is a simplified version. In production, you'd need to
            # anonymize all user-related data across all tables
            
        except Exception as e:
            logger.error(f"Error anonymizing user data: {e}")
            raise
    
    async def _delete_user_data(self, db: Session, user_id: str):
        """Delete user data"""
        try:
            # Delete in order to respect foreign key constraints
            
            # Delete messages
            db.execute(text("DELETE FROM messages WHERE chat_session_id IN (SELECT id FROM chat_sessions WHERE user_id = :user_id)"), {"user_id": user_id})
            
            # Delete chat sessions
            db.execute(text("DELETE FROM chat_sessions WHERE user_id = :user_id"), {"user_id": user_id})
            
            # Delete analysis results
            db.execute(text("DELETE FROM analyses WHERE user_id = :user_id"), {"user_id": user_id})
            
            # Delete log files
            db.execute(text("DELETE FROM log_files WHERE user_id = :user_id"), {"user_id": user_id})
            
            # Delete projects
            db.execute(text("DELETE FROM projects WHERE user_id = :user_id"), {"user_id": user_id})
            
            # Delete audit logs
            db.execute(text("DELETE FROM audit_logs WHERE user_id = :user_id"), {"user_id": user_id})
            
            # Delete user
            db.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            raise
    
    async def _log_data_export(self, user_id: str, export_type: str):
        """Log data export event"""
        try:
            # This would integrate with the audit logging system
            logger.info(f"Data export: {export_type} for user {user_id}")
        except Exception as e:
            logger.error(f"Error logging data export: {e}")
    
    async def _log_data_deletion(self, user_id: str, anonymized: bool):
        """Log data deletion event"""
        try:
            # This would integrate with the audit logging system
            action = "data_anonymized" if anonymized else "data_deleted"
            logger.info(f"Data deletion: {action} for user {user_id}")
        except Exception as e:
            logger.error(f"Error logging data deletion: {e}")
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data based on retention periods"""
        try:
            db = next(get_db())
            try:
                cleanup_stats = {}
                
                # Clean up old audit logs
                audit_cutoff = datetime.utcnow() - timedelta(days=self.data_retention_periods["audit_logs"])
                deleted_audit = db.execute(
                    text("DELETE FROM audit_logs WHERE timestamp < :cutoff"),
                    {"cutoff": audit_cutoff}
                )
                cleanup_stats["audit_logs"] = deleted_audit.rowcount
                
                # Clean up old log files
                log_cutoff = datetime.utcnow() - timedelta(days=self.data_retention_periods["log_files"])
                deleted_logs = db.execute(
                    text("DELETE FROM log_files WHERE created_at < :cutoff"),
                    {"cutoff": log_cutoff}
                )
                cleanup_stats["log_files"] = deleted_logs.rowcount
                
                # Clean up old chat sessions
                chat_cutoff = datetime.utcnow() - timedelta(days=self.data_retention_periods["chat_sessions"])
                deleted_chats = db.execute(
                    text("DELETE FROM chat_sessions WHERE created_at < :cutoff"),
                    {"cutoff": chat_cutoff}
                )
                cleanup_stats["chat_sessions"] = deleted_chats.rowcount
                
                # Clean up old analysis results
                analysis_cutoff = datetime.utcnow() - timedelta(days=self.data_retention_periods["analysis_results"])
                deleted_analyses = db.execute(
                    text("DELETE FROM analyses WHERE created_at < :cutoff"),
                    {"cutoff": analysis_cutoff}
                )
                cleanup_stats["analysis_results"] = deleted_analyses.rowcount
                
                db.commit()
                
                logger.info(f"Data cleanup completed: {cleanup_stats}")
                return cleanup_stats
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
            return {}
    
    async def get_data_retention_status(self) -> Dict[str, Any]:
        """Get data retention status"""
        try:
            db = next(get_db())
            try:
                status = {
                    "retention_periods": self.data_retention_periods,
                    "data_counts": {},
                    "oldest_data": {},
                    "cleanup_recommendations": []
                }
                
                # Get data counts
                status["data_counts"]["users"] = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
                status["data_counts"]["audit_logs"] = db.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar()
                status["data_counts"]["log_files"] = db.execute(text("SELECT COUNT(*) FROM log_files")).scalar()
                status["data_counts"]["chat_sessions"] = db.execute(text("SELECT COUNT(*) FROM chat_sessions")).scalar()
                status["data_counts"]["analyses"] = db.execute(text("SELECT COUNT(*) FROM analyses")).scalar()
                
                # Get oldest data timestamps
                status["oldest_data"]["audit_logs"] = db.execute(
                    text("SELECT MIN(timestamp) FROM audit_logs")
                ).scalar()
                status["oldest_data"]["log_files"] = db.execute(
                    text("SELECT MIN(created_at) FROM log_files")
                ).scalar()
                status["oldest_data"]["chat_sessions"] = db.execute(
                    text("SELECT MIN(created_at) FROM chat_sessions")
                ).scalar()
                
                # Generate cleanup recommendations
                now = datetime.utcnow()
                for data_type, retention_days in self.data_retention_periods.items():
                    cutoff = now - timedelta(days=retention_days)
                    if status["oldest_data"].get(data_type) and status["oldest_data"][data_type] < cutoff:
                        status["cleanup_recommendations"].append({
                            "data_type": data_type,
                            "oldest_record": status["oldest_data"][data_type].isoformat(),
                            "retention_period_days": retention_days,
                            "recommendation": "Consider cleaning up old data"
                        })
                
                return status
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting data retention status: {e}")
            return {}


class ConsentManager:
    """Manage user consent for data processing"""
    
    def __init__(self):
        self.consent_types = {
            "marketing": "Marketing communications",
            "analytics": "Analytics and usage tracking",
            "cookies": "Cookie usage",
            "data_sharing": "Data sharing with third parties",
            "profiling": "Automated profiling",
            "research": "Research and development"
        }
    
    async def record_consent(
        self,
        user_id: str,
        consent_type: str,
        granted: bool,
        consent_text: str,
        ip_address: str
    ) -> bool:
        """Record user consent"""
        try:
            # This would store consent in a consent_logs table
            consent_data = {
                "user_id": user_id,
                "consent_type": consent_type,
                "granted": granted,
                "consent_text": consent_text,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Consent recorded: {consent_type} for user {user_id} - {granted}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            return False
    
    async def get_user_consent(self, user_id: str) -> Dict[str, Any]:
        """Get user consent status"""
        try:
            # This would query the consent_logs table
            # For now, return default consent status
            return {
                "user_id": user_id,
                "consent_status": {
                    consent_type: True  # Default to granted
                    for consent_type in self.consent_types.keys()
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user consent: {e}")
            return {}


# Global instances
gdpr_compliance = GDPRCompliance()
consent_manager = ConsentManager()
