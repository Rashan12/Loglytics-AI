-- Performance optimization indexes for Loglytics AI
-- These indexes are designed to optimize common query patterns

-- Composite indexes for common query patterns

-- Log entries queries by project and time range
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_project_timestamp 
ON log_entries (project_id, timestamp DESC);

-- Log entries queries by project and log level
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_project_level 
ON log_entries (project_id, log_level) WHERE log_level IS NOT NULL;

-- Log entries queries by project and source
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_project_source 
ON log_entries (project_id, source) WHERE source IS NOT NULL;

-- Log entries full-text search on message content
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_message_gin 
ON log_entries USING gin (to_tsvector('english', message));

-- Log entries JSONB metadata queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_metadata_gin 
ON log_entries USING gin (metadata) WHERE metadata IS NOT NULL;

-- RAG vectors similarity search optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rag_vectors_project_embedding 
ON rag_vectors (project_id, embedding vector_cosine_ops);

-- Analytics cache queries by type and project
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_cache_project_type 
ON analytics_cache (project_id, analytics_type);

-- Analytics cache queries by log file
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_cache_log_file 
ON analytics_cache (log_file_id, created_at DESC);

-- Alerts queries by user and read status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_user_read 
ON alerts (user_id, is_read, created_at DESC);

-- Alerts queries by severity and project
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_severity_project 
ON alerts (severity, project_id, created_at DESC);

-- Audit logs queries by user and action
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_action 
ON audit_logs (user_id, action, created_at DESC);

-- Audit logs queries by resource type
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource 
ON audit_logs (resource_type, resource_id, created_at DESC);

-- Usage tracking queries by user and date range
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_tracking_user_date 
ON usage_tracking (user_id, date DESC);

-- Project shares queries by shared user
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_project_shares_shared_with 
ON project_shares (shared_with_user_id, project_id);

-- Project shares queries by shared by user
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_project_shares_shared_by 
ON project_shares (shared_by_user_id, project_id);

-- Webhooks queries by project and active status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_webhooks_project_active 
ON webhooks (project_id, is_active) WHERE is_active = true;

-- Live log connections queries by project and status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_live_connections_project_status 
ON live_log_connections (project_id, status);

-- API keys queries by user and active status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_user_active 
ON api_keys (user_id, is_active) WHERE is_active = true;

-- API keys queries by expiration
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_expires 
ON api_keys (expires_at) WHERE expires_at IS NOT NULL;

-- Chats queries by project and user
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chats_project_user 
ON chats (project_id, user_id, created_at DESC);

-- Messages queries by chat and created date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_chat_created 
ON messages (chat_id, created_at DESC);

-- Log files queries by project and upload status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_files_project_status 
ON log_files (project_id, upload_status, created_at DESC);

-- Log files queries by user and file type
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_files_user_type 
ON log_files (user_id, file_type) WHERE file_type IS NOT NULL;

-- Partial indexes for common filtered queries

-- Active users only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active 
ON users (id, email) WHERE is_active = true;

-- Completed log files only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_files_completed 
ON log_files (project_id, created_at DESC) WHERE upload_status = 'completed';

-- Unread alerts only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_unread 
ON alerts (user_id, created_at DESC) WHERE is_read = false;

-- Active webhooks only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_webhooks_active 
ON webhooks (project_id, created_at DESC) WHERE is_active = true;

-- Active API keys only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_active 
ON api_keys (user_id, created_at DESC) WHERE is_active = true;

-- Recent audit logs (last 30 days)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_recent 
ON audit_logs (user_id, created_at DESC) 
WHERE created_at > NOW() - INTERVAL '30 days';

-- Statistics and monitoring queries

-- User activity summary
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_activity 
ON users (created_at, is_active);

-- Project activity summary
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_activity 
ON projects (user_id, created_at DESC);

-- Log entry volume by day (for TimescaleDB)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_daily_volume 
ON log_entries (date_trunc('day', timestamp), project_id);

-- Error rate monitoring
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_errors 
ON log_entries (project_id, timestamp DESC) 
WHERE log_level IN ('ERROR', 'CRITICAL');

-- Performance monitoring queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_performance 
ON log_entries (project_id, timestamp DESC, log_level) 
WHERE log_level IN ('WARN', 'ERROR', 'CRITICAL');

-- Text search optimization for log messages
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_entries_message_trgm 
ON log_entries USING gin (message gin_trgm_ops);

-- Enable trigram extension for text search if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create a materialized view for dashboard statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_stats AS
SELECT 
    p.id as project_id,
    p.user_id,
    p.name as project_name,
    COUNT(DISTINCT lf.id) as total_log_files,
    COUNT(le.id) as total_log_entries,
    COUNT(le.id) FILTER (WHERE le.log_level = 'ERROR') as error_count,
    COUNT(le.id) FILTER (WHERE le.log_level = 'WARN') as warning_count,
    COUNT(le.id) FILTER (WHERE le.log_level = 'INFO') as info_count,
    COUNT(le.id) FILTER (WHERE le.log_level = 'DEBUG') as debug_count,
    COUNT(le.id) FILTER (WHERE le.log_level = 'CRITICAL') as critical_count,
    MAX(le.timestamp) as last_log_entry,
    MIN(le.timestamp) as first_log_entry
FROM projects p
LEFT JOIN log_files lf ON p.id = lf.project_id
LEFT JOIN log_entries le ON lf.id = le.log_file_id
GROUP BY p.id, p.user_id, p.name;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_dashboard_stats_project 
ON dashboard_stats (project_id);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;
END;
$$;

-- Create a function to get user's accessible projects
CREATE OR REPLACE FUNCTION get_user_accessible_projects(user_uuid UUID)
RETURNS TABLE(project_id UUID, project_name TEXT, user_role TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id as project_id,
        p.name as project_name,
        'owner'::TEXT as user_role
    FROM projects p
    WHERE p.user_id = user_uuid
    
    UNION
    
    SELECT 
        p.id as project_id,
        p.name as project_name,
        ps.role::TEXT as user_role
    FROM projects p
    JOIN project_shares ps ON p.id = ps.project_id
    WHERE ps.shared_with_user_id = user_uuid;
END;
$$;
