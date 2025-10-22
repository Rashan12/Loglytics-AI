"""
Comprehensive Audit Logging System
Logs all sensitive operations for security and compliance
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)


class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.sensitive_operations = {
            "user_login", "user_logout", "user_register", "password_change",
            "password_reset", "api_key_create", "api_key_revoke", "api_key_update",
            "file_upload", "file_delete", "file_download", "project_share",
            "project_unshare", "settings_change", "user_delete", "user_update",
            "role_change", "permission_change", "webhook_create", "webhook_update",
            "webhook_delete", "webhook_test", "alert_create", "alert_update",
            "alert_delete", "analysis_create", "analysis_delete", "chat_create",
            "chat_delete", "llm_request", "rag_query", "live_log_connect",
            "live_log_disconnect", "notification_send", "notification_read",
            "notification_delete", "backup_create", "backup_restore",
            "system_config_change", "security_event", "data_export", "data_import"
        }
        
        self.sensitive_endpoints = {
            "/api/v1/auth/login": "user_login",
            "/api/v1/auth/logout": "user_logout",
            "/api/v1/auth/register": "user_register",
            "/api/v1/auth/password-reset": "password_reset",
            "/api/v1/auth/change-password": "password_change",
            "/api/v1/api-keys": "api_key_management",
            "/api/v1/upload": "file_upload",
            "/api/v1/logs": "file_management",
            "/api/v1/projects/share": "project_share",
            "/api/v1/settings": "settings_change",
            "/api/v1/users": "user_management",
            "/api/v1/webhooks": "webhook_management",
            "/api/v1/alerts": "alert_management",
            "/api/v1/analytics": "analysis_management",
            "/api/v1/chat": "chat_management",
            "/api/v1/llm": "llm_request",
            "/api/v1/rag": "rag_query",
            "/api/v1/live-logs": "live_log_management",
            "/api/v1/notifications": "notification_management",
            "/api/v1/backup": "backup_management",
            "/api/v1/admin": "admin_operations"
        }
    
    async def log_operation(
        self,
        operation: str,
        user_id: Optional[str],
        resource_type: str,
        resource_id: Optional[str],
        request: Optional[Request] = None,
        response: Optional[Response] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Log a sensitive operation
        
        Args:
            operation: Type of operation
            user_id: User ID (None for system operations)
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            request: FastAPI request object
            response: FastAPI response object
            metadata: Additional metadata
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Audit log ID
        """
        try:
            # Generate audit log ID
            audit_id = str(uuid.uuid4())
            
            # Extract request info if available
            if request:
                ip_address = ip_address or self._get_client_ip(request)
                user_agent = user_agent or request.headers.get("user-agent", "")
                path = request.url.path
                method = request.method
                query_params = dict(request.query_params)
            else:
                path = ""
                method = ""
                query_params = {}
            
            # Extract response info if available
            status_code = response.status_code if response else None
            
            # Prepare audit log data
            audit_data = {
                "id": audit_id,
                "operation": operation,
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "path": path,
                "method": method,
                "status_code": status_code,
                "query_params": query_params,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Store in database
            await self._store_audit_log(audit_data)
            
            # Log to application logger
            logger.info(f"Audit: {operation} by user {user_id} on {resource_type} {resource_id}")
            
            return audit_id
            
        except Exception as e:
            logger.error(f"Error logging audit operation: {e}")
            return ""
    
    async def log_authentication_event(
        self,
        event_type: str,
        user_id: Optional[str],
        success: bool,
        request: Request,
        failure_reason: Optional[str] = None
    ) -> str:
        """Log authentication events"""
        metadata = {
            "success": success,
            "failure_reason": failure_reason,
            "event_type": event_type
        }
        
        return await self.log_operation(
            operation=event_type,
            user_id=user_id,
            resource_type="authentication",
            resource_id=user_id,
            request=request,
            metadata=metadata
        )
    
    async def log_file_operation(
        self,
        operation: str,
        user_id: str,
        file_id: str,
        filename: str,
        file_size: int,
        request: Request,
        success: bool = True
    ) -> str:
        """Log file operations"""
        metadata = {
            "filename": filename,
            "file_size": file_size,
            "success": success
        }
        
        return await self.log_operation(
            operation=operation,
            user_id=user_id,
            resource_type="file",
            resource_id=file_id,
            request=request,
            metadata=metadata
        )
    
    async def log_api_key_operation(
        self,
        operation: str,
        user_id: str,
        api_key_id: str,
        request: Request,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log API key operations"""
        return await self.log_operation(
            operation=operation,
            user_id=user_id,
            resource_type="api_key",
            resource_id=api_key_id,
            request=request,
            metadata=metadata
        )
    
    async def log_project_operation(
        self,
        operation: str,
        user_id: str,
        project_id: str,
        request: Request,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log project operations"""
        return await self.log_operation(
            operation=operation,
            user_id=user_id,
            resource_type="project",
            resource_id=project_id,
            request=request,
            metadata=metadata
        )
    
    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str],
        ip_address: str,
        description: str,
        severity: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log security events"""
        security_metadata = {
            "description": description,
            "severity": severity,
            "event_type": event_type
        }
        if metadata:
            security_metadata.update(metadata)
        
        return await self.log_operation(
            operation="security_event",
            user_id=user_id,
            resource_type="security",
            resource_id=str(uuid.uuid4()),
            metadata=security_metadata,
            ip_address=ip_address
        )
    
    async def log_data_operation(
        self,
        operation: str,
        user_id: str,
        data_type: str,
        record_count: int,
        request: Request,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log data operations (export, import, delete)"""
        data_metadata = {
            "data_type": data_type,
            "record_count": record_count
        }
        if metadata:
            data_metadata.update(metadata)
        
        return await self.log_operation(
            operation=operation,
            user_id=user_id,
            resource_type="data",
            resource_id=str(uuid.uuid4()),
            request=request,
            metadata=data_metadata
        )
    
    async def log_system_event(
        self,
        operation: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log system events"""
        system_metadata = {
            "description": description,
            "system_event": True
        }
        if metadata:
            system_metadata.update(metadata)
        
        return await self.log_operation(
            operation=operation,
            user_id=None,  # System operation
            resource_type="system",
            resource_id=str(uuid.uuid4()),
            metadata=system_metadata
        )
    
    async def _store_audit_log(self, audit_data: Dict[str, Any]):
        """Store audit log in database"""
        try:
            db = next(get_db())
            try:
                audit_log = AuditLog(
                    id=audit_data["id"],
                    operation=audit_data["operation"],
                    user_id=audit_data["user_id"],
                    resource_type=audit_data["resource_type"],
                    resource_id=audit_data["resource_id"],
                    ip_address=audit_data["ip_address"],
                    user_agent=audit_data["user_agent"],
                    path=audit_data["path"],
                    method=audit_data["method"],
                    status_code=audit_data["status_code"],
                    query_params=audit_data["query_params"],
                    metadata=audit_data["metadata"],
                    timestamp=audit_data["timestamp"]
                )
                
                db.add(audit_log)
                db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error storing audit log: {e}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""
        try:
            db = next(get_db())
            try:
                query = db.query(AuditLog)
                
                if user_id:
                    query = query.filter(AuditLog.user_id == user_id)
                
                if operation:
                    query = query.filter(AuditLog.operation == operation)
                
                if resource_type:
                    query = query.filter(AuditLog.resource_type == resource_type)
                
                if start_date:
                    query = query.filter(AuditLog.timestamp >= start_date)
                
                if end_date:
                    query = query.filter(AuditLog.timestamp <= end_date)
                
                # Order by timestamp descending
                query = query.order_by(AuditLog.timestamp.desc())
                
                # Apply pagination
                query = query.offset(offset).limit(limit)
                
                logs = query.all()
                
                return [
                    {
                        "id": log.id,
                        "operation": log.operation,
                        "user_id": log.user_id,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "path": log.path,
                        "method": log.method,
                        "status_code": log.status_code,
                        "query_params": log.query_params,
                        "metadata": log.metadata,
                        "timestamp": log.timestamp.isoformat()
                    }
                    for log in logs
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    async def cleanup_old_logs(self, days_to_keep: int = 90):
        """Clean up old audit logs"""
        try:
            db = next(get_db())
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                
                # Delete old logs
                result = db.execute(
                    text("DELETE FROM audit_logs WHERE timestamp < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                
                deleted_count = result.rowcount
                db.commit()
                
                logger.info(f"Cleaned up {deleted_count} old audit logs")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
    
    async def export_audit_logs(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Export audit logs for compliance"""
        try:
            logs = await self.get_audit_logs(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Large limit for export
            )
            
            # Add export metadata
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "exported_by": user_id,
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "total_records": len(logs),
                "logs": logs
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}")
            return {}


class AuditMiddleware:
    """Middleware to automatically log sensitive operations"""
    
    def __init__(self, app):
        self.app = app
        self.audit_logger = AuditLogger()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            # Process request
            response = await self.app(scope, receive, send)
            
            # Log sensitive operations
            await self._log_request(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in audit middleware: {e}")
            return await self.app(scope, receive, send)
    
    async def _log_request(self, request: Request, response: Response):
        """Log request if it's a sensitive operation"""
        try:
            path = request.url.path
            method = request.method
            status_code = response.status_code if response else None
            
            # Check if this is a sensitive endpoint
            operation = self.audit_logger.sensitive_endpoints.get(path)
            if not operation:
                return
            
            # Get user ID from request state (set by auth middleware)
            user_id = getattr(request.state, "user_id", None)
            
            # Determine resource type and ID from path
            resource_type, resource_id = self._extract_resource_info(path)
            
            # Log the operation
            await self.audit_logger.log_operation(
                operation=operation,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                request=request,
                response=response
            )
            
        except Exception as e:
            logger.error(f"Error logging request: {e}")
    
    def _extract_resource_info(self, path: str) -> tuple[str, Optional[str]]:
        """Extract resource type and ID from path"""
        path_parts = path.strip("/").split("/")
        
        if len(path_parts) >= 3:
            resource_type = path_parts[2]  # e.g., "users", "projects", "logs"
            if len(path_parts) >= 4 and path_parts[3].isdigit():
                resource_id = path_parts[3]
            else:
                resource_id = None
        else:
            resource_type = "unknown"
            resource_id = None
        
        return resource_type, resource_id


# Global audit logger instance
audit_logger = AuditLogger()


def create_audit_middleware():
    """Create audit middleware"""
    return AuditMiddleware
