-- Complete database setup script for Loglytics AI
-- This script sets up the database with all extensions, tables, and policies

-- Create database (run as superuser)
-- CREATE DATABASE loglytics_db;
-- \c loglytics_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Verify extensions
SELECT extname, extversion 
FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'vector', 'timescaledb', 'pg_trgm');

-- Create custom types
DO $$ BEGIN
    CREATE TYPE subscription_tier AS ENUM ('free', 'pro');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE llm_model AS ENUM ('local', 'maverick');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE upload_status AS ENUM ('uploading', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE log_level AS ENUM ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE cloud_provider AS ENUM ('aws', 'azure', 'gcp');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE connection_status AS ENUM ('active', 'paused', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_type AS ENUM ('error_threshold', 'anomaly', 'pattern_match');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE share_role AS ENUM ('viewer', 'editor', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create auth schema and function (placeholder for auth system integration)
CREATE SCHEMA IF NOT EXISTS auth;

CREATE OR REPLACE FUNCTION auth.uid()
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- This should be replaced with your actual auth system integration
    -- For now, returning NULL as a placeholder
    RETURN NULL;
END;
$$;

-- Create tables (these will be created by Alembic migrations)
-- This is just a reference - actual table creation is handled by migrations

-- Create a function to check if user has access to project
CREATE OR REPLACE FUNCTION user_has_project_access(user_uuid UUID, project_uuid UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM projects p
        WHERE p.id = project_uuid AND p.user_id = user_uuid
        
        UNION
        
        SELECT 1 FROM project_shares ps
        WHERE ps.project_id = project_uuid AND ps.shared_with_user_id = user_uuid
    );
END;
$$;

-- Create a function to get user's role in project
CREATE OR REPLACE FUNCTION get_user_project_role(user_uuid UUID, project_uuid UUID)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    user_role TEXT;
BEGIN
    -- Check if user is owner
    IF EXISTS (SELECT 1 FROM projects WHERE id = project_uuid AND user_id = user_uuid) THEN
        RETURN 'owner';
    END IF;
    
    -- Check if user has shared access
    SELECT ps.role::TEXT INTO user_role
    FROM project_shares ps
    WHERE ps.project_id = project_uuid AND ps.shared_with_user_id = user_uuid
    LIMIT 1;
    
    RETURN COALESCE(user_role, 'none');
END;
$$;

-- Create a function to log user actions
CREATE OR REPLACE FUNCTION log_user_action(
    p_user_id UUID,
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id UUID DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    log_id UUID;
BEGIN
    INSERT INTO audit_logs (
        user_id, action, resource_type, resource_id, metadata, ip_address
    ) VALUES (
        p_user_id, p_action, p_resource_type, p_resource_id, p_metadata, p_ip_address
    ) RETURNING id INTO log_id;
    
    RETURN log_id;
END;
$$;

-- Create a function to update usage tracking
CREATE OR REPLACE FUNCTION update_usage_tracking(
    p_user_id UUID,
    p_date DATE,
    p_llm_tokens_used BIGINT DEFAULT 0,
    p_api_calls_count INTEGER DEFAULT 0,
    p_storage_used_bytes BIGINT DEFAULT 0
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO usage_tracking (
        user_id, date, llm_tokens_used, api_calls_count, storage_used_bytes
    ) VALUES (
        p_user_id, p_date, p_llm_tokens_used, p_api_calls_count, p_storage_used_bytes
    )
    ON CONFLICT (user_id, date) 
    DO UPDATE SET
        llm_tokens_used = usage_tracking.llm_tokens_used + p_llm_tokens_used,
        api_calls_count = usage_tracking.api_calls_count + p_api_calls_count,
        storage_used_bytes = GREATEST(usage_tracking.storage_used_bytes, p_storage_used_bytes),
        updated_at = NOW();
END;
$$;

-- Create a function to search log entries with full-text search
CREATE OR REPLACE FUNCTION search_log_entries(
    p_project_id UUID,
    p_search_query TEXT,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    timestamp TIMESTAMPTZ,
    log_level log_level,
    message TEXT,
    source TEXT,
    metadata JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        le.id,
        le.timestamp,
        le.log_level,
        le.message,
        le.source,
        le.metadata
    FROM log_entries le
    WHERE le.project_id = p_project_id
    AND (
        le.message ILIKE '%' || p_search_query || '%'
        OR le.source ILIKE '%' || p_search_query || '%'
        OR to_tsvector('english', le.message) @@ plainto_tsquery('english', p_search_query)
    )
    ORDER BY le.timestamp DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;

-- Create a function to get project statistics
CREATE OR REPLACE FUNCTION get_project_stats(p_project_id UUID)
RETURNS TABLE (
    total_log_files BIGINT,
    total_log_entries BIGINT,
    error_count BIGINT,
    warning_count BIGINT,
    info_count BIGINT,
    debug_count BIGINT,
    critical_count BIGINT,
    last_log_entry TIMESTAMPTZ,
    first_log_entry TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT lf.id) as total_log_files,
        COUNT(le.id) as total_log_entries,
        COUNT(le.id) FILTER (WHERE le.log_level = 'ERROR') as error_count,
        COUNT(le.id) FILTER (WHERE le.log_level = 'WARN') as warning_count,
        COUNT(le.id) FILTER (WHERE le.log_level = 'INFO') as info_count,
        COUNT(le.id) FILTER (WHERE le.log_level = 'DEBUG') as debug_count,
        COUNT(le.id) FILTER (WHERE le.log_level = 'CRITICAL') as critical_count,
        MAX(le.timestamp) as last_log_entry,
        MIN(le.timestamp) as first_log_entry
    FROM log_files lf
    LEFT JOIN log_entries le ON lf.id = le.log_file_id
    WHERE lf.project_id = p_project_id;
END;
$$;

-- Create a function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Delete old audit logs (older than 1 year)
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '1 year';
    
    -- Delete old completed log files (older than 2 years)
    DELETE FROM log_files 
    WHERE upload_status = 'completed' 
    AND created_at < NOW() - INTERVAL '2 years';
    
    -- Delete old usage tracking data (older than 2 years)
    DELETE FROM usage_tracking 
    WHERE date < CURRENT_DATE - INTERVAL '2 years';
END;
$$;

-- Create a scheduled job to run cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data();');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA auth TO PUBLIC;
GRANT EXECUTE ON FUNCTION auth.uid() TO PUBLIC;
GRANT EXECUTE ON FUNCTION user_has_project_access(UUID, UUID) TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_user_project_role(UUID, UUID) TO PUBLIC;
GRANT EXECUTE ON FUNCTION log_user_action(UUID, TEXT, TEXT, UUID, JSONB, INET) TO PUBLIC;
GRANT EXECUTE ON FUNCTION update_usage_tracking(UUID, DATE, BIGINT, INTEGER, BIGINT) TO PUBLIC;
GRANT EXECUTE ON FUNCTION search_log_entries(UUID, TEXT, INTEGER, INTEGER) TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_project_stats(UUID) TO PUBLIC;
GRANT EXECUTE ON FUNCTION cleanup_old_data() TO PUBLIC;

-- Create a view for user dashboard data
CREATE OR REPLACE VIEW user_dashboard AS
SELECT 
    u.id as user_id,
    u.email,
    u.subscription_tier,
    COUNT(DISTINCT p.id) as total_projects,
    COUNT(DISTINCT lf.id) as total_log_files,
    COUNT(le.id) as total_log_entries,
    COUNT(le.id) FILTER (WHERE le.log_level = 'ERROR') as error_count,
    COUNT(le.id) FILTER (WHERE le.log_level = 'WARN') as warning_count,
    COUNT(a.id) FILTER (WHERE a.is_read = false) as unread_alerts,
    MAX(le.timestamp) as last_log_entry,
    MAX(p.created_at) as last_project_created
FROM users u
LEFT JOIN projects p ON u.id = p.user_id
LEFT JOIN log_files lf ON p.id = lf.project_id
LEFT JOIN log_entries le ON lf.id = le.log_file_id
LEFT JOIN alerts a ON u.id = a.user_id
GROUP BY u.id, u.email, u.subscription_tier;

-- Grant access to the view
GRANT SELECT ON user_dashboard TO PUBLIC;

-- Create indexes for performance (these will be created by the performance_indexes.sql script)
-- The actual indexes are in the separate performance_indexes.sql file

-- Final verification
SELECT 'Database setup completed successfully' as status;
