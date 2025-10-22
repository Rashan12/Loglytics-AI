-- Row-Level Security (RLS) policies for Loglytics AI
-- This script sets up RLS policies for multi-tenant data isolation

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_vectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_log_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- Users table policies
-- Users can only see and modify their own records
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Projects table policies
-- Users can only see projects they own or have been shared
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (
        user_id = auth.uid() OR 
        id IN (
            SELECT project_id FROM project_shares 
            WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own projects" ON projects
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (user_id = auth.uid());

-- Chats table policies
-- Users can only see chats in their projects
CREATE POLICY "Users can view chats in accessible projects" ON chats
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create chats in own projects" ON chats
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own chats" ON chats
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own chats" ON chats
    FOR DELETE USING (user_id = auth.uid());

-- Messages table policies
-- Users can only see messages in their chats
CREATE POLICY "Users can view messages in accessible chats" ON messages
    FOR SELECT USING (
        chat_id IN (
            SELECT id FROM chats WHERE user_id = auth.uid()
            UNION
            SELECT c.id FROM chats c
            JOIN project_shares ps ON c.project_id = ps.project_id
            WHERE ps.shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages in own chats" ON messages
    FOR INSERT WITH CHECK (
        chat_id IN (SELECT id FROM chats WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own messages" ON messages
    FOR UPDATE USING (
        chat_id IN (SELECT id FROM chats WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can delete own messages" ON messages
    FOR DELETE USING (
        chat_id IN (SELECT id FROM chats WHERE user_id = auth.uid())
    );

-- Log files table policies
-- Users can only see log files in their projects
CREATE POLICY "Users can view log files in accessible projects" ON log_files
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create log files in own projects" ON log_files
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own log files" ON log_files
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own log files" ON log_files
    FOR DELETE USING (user_id = auth.uid());

-- Log entries table policies
-- Users can only see log entries in their projects
CREATE POLICY "Users can view log entries in accessible projects" ON log_entries
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create log entries in own projects" ON log_entries
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own log entries" ON log_entries
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own log entries" ON log_entries
    FOR DELETE USING (user_id = auth.uid());

-- RAG vectors table policies
-- Users can only see vectors in their projects
CREATE POLICY "Users can view vectors in accessible projects" ON rag_vectors
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create vectors in own projects" ON rag_vectors
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own vectors" ON rag_vectors
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own vectors" ON rag_vectors
    FOR DELETE USING (user_id = auth.uid());

-- Analytics cache table policies
-- Users can only see analytics in their projects
CREATE POLICY "Users can view analytics in accessible projects" ON analytics_cache
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create analytics in own projects" ON analytics_cache
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own analytics" ON analytics_cache
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own analytics" ON analytics_cache
    FOR DELETE USING (user_id = auth.uid());

-- Live log connections table policies
-- Users can only see connections in their projects
CREATE POLICY "Users can view connections in accessible projects" ON live_log_connections
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create connections in own projects" ON live_log_connections
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own connections" ON live_log_connections
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own connections" ON live_log_connections
    FOR DELETE USING (user_id = auth.uid());

-- Alerts table policies
-- Users can only see their own alerts
CREATE POLICY "Users can view own alerts" ON alerts
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create own alerts" ON alerts
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own alerts" ON alerts
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own alerts" ON alerts
    FOR DELETE USING (user_id = auth.uid());

-- API keys table policies
-- Users can only see their own API keys
CREATE POLICY "Users can view own API keys" ON api_keys
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create own API keys" ON api_keys
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own API keys" ON api_keys
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own API keys" ON api_keys
    FOR DELETE USING (user_id = auth.uid());

-- Audit logs table policies
-- Users can only see their own audit logs
CREATE POLICY "Users can view own audit logs" ON audit_logs
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create own audit logs" ON audit_logs
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Project shares table policies
-- Users can see shares they gave or received
CREATE POLICY "Users can view relevant project shares" ON project_shares
    FOR SELECT USING (
        shared_by_user_id = auth.uid() OR shared_with_user_id = auth.uid()
    );

CREATE POLICY "Users can create project shares" ON project_shares
    FOR INSERT WITH CHECK (
        shared_by_user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update project shares they created" ON project_shares
    FOR UPDATE USING (shared_by_user_id = auth.uid());

CREATE POLICY "Users can delete project shares they created" ON project_shares
    FOR DELETE USING (shared_by_user_id = auth.uid());

-- Webhooks table policies
-- Users can only see webhooks in their projects
CREATE POLICY "Users can view webhooks in accessible projects" ON webhooks
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
            UNION
            SELECT project_id FROM project_shares WHERE shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create webhooks in own projects" ON webhooks
    FOR INSERT WITH CHECK (
        user_id = auth.uid() AND
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update own webhooks" ON webhooks
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own webhooks" ON webhooks
    FOR DELETE USING (user_id = auth.uid());

-- Usage tracking table policies
-- Users can only see their own usage data
CREATE POLICY "Users can view own usage tracking" ON usage_tracking
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create own usage tracking" ON usage_tracking
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own usage tracking" ON usage_tracking
    FOR UPDATE USING (user_id = auth.uid());

-- Create a function to get current user ID (for use with auth.uid())
-- This is a placeholder - in production, you would integrate with your auth system
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- This should return the current user's UUID from your auth system
    -- For now, returning a placeholder
    RETURN NULL;
END;
$$;
