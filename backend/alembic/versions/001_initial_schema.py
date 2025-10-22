"""Initial schema with pgvector and TimescaleDB

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "timescaledb"')
    
    # Create enums
    op.execute("""
        CREATE TYPE subscription_tier AS ENUM ('free', 'pro')
    """)
    
    op.execute("""
        CREATE TYPE llm_model AS ENUM ('local', 'maverick')
    """)
    
    op.execute("""
        CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system')
    """)
    
    op.execute("""
        CREATE TYPE upload_status AS ENUM ('uploading', 'processing', 'completed', 'failed')
    """)
    
    op.execute("""
        CREATE TYPE log_level AS ENUM ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    """)
    
    op.execute("""
        CREATE TYPE cloud_provider AS ENUM ('aws', 'azure', 'gcp')
    """)
    
    op.execute("""
        CREATE TYPE connection_status AS ENUM ('active', 'paused', 'error')
    """)
    
    op.execute("""
        CREATE TYPE alert_type AS ENUM ('error_threshold', 'anomaly', 'pattern_match')
    """)
    
    op.execute("""
        CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical')
    """)
    
    op.execute("""
        CREATE TYPE share_role AS ENUM ('viewer', 'editor', 'admin')
    """)

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('subscription_tier', postgresql.ENUM('free', 'pro', name='subscription_tier'), nullable=False, default='free'),
        sa.Column('selected_llm_model', postgresql.ENUM('local', 'maverick', name='llm_model'), nullable=False, default='local'),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for users
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_subscription_tier', 'users', ['subscription_tier'])

    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for projects
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # Create chats table
    op.create_table('chats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for chats
    op.create_index('ix_chats_project_id', 'chats', ['project_id'])
    op.create_index('ix_chats_user_id', 'chats', ['user_id'])

    # Create messages table
    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('chat_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chats.id'), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'system', name='message_role'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for messages
    op.create_index('ix_messages_chat_id', 'messages', ['chat_id'])

    # Create log_files table
    op.create_table('log_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('chat_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chats.id'), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.BigInteger, nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('s3_key', sa.Text, nullable=True),
        sa.Column('upload_status', postgresql.ENUM('uploading', 'processing', 'completed', 'failed', name='upload_status'), nullable=False, default='uploading'),
        sa.Column('processing_metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for log_files
    op.create_index('ix_log_files_project_id', 'log_files', ['project_id'])
    op.create_index('ix_log_files_user_id', 'log_files', ['user_id'])
    op.create_index('ix_log_files_upload_status', 'log_files', ['upload_status'])

    # Create log_entries table (will be converted to hypertable)
    op.create_table('log_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('log_file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('log_files.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('log_level', postgresql.ENUM('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL', name='log_level'), nullable=True),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('raw_content', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for log_entries
    op.create_index('ix_log_entries_log_file_id', 'log_entries', ['log_file_id'])
    op.create_index('ix_log_entries_project_id', 'log_entries', ['project_id'])
    op.create_index('ix_log_entries_user_id', 'log_entries', ['user_id'])
    op.create_index('ix_log_entries_log_level', 'log_entries', ['log_level'])
    op.create_index('ix_log_entries_timestamp', 'log_entries', ['timestamp'])
    op.create_index('ix_log_entries_created_at', 'log_entries', ['created_at'])

    # Convert log_entries to TimescaleDB hypertable
    op.execute("SELECT create_hypertable('log_entries', 'timestamp')")

    # Create rag_vectors table
    op.create_table('rag_vectors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('log_file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('log_files.id'), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float), nullable=False),  # Will be converted to vector(384)
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for rag_vectors
    op.create_index('ix_rag_vectors_project_id', 'rag_vectors', ['project_id'])
    op.create_index('ix_rag_vectors_user_id', 'rag_vectors', ['user_id'])
    op.create_index('ix_rag_vectors_log_file_id', 'rag_vectors', ['log_file_id'])

    # Convert embedding column to vector type and create vector index
    op.execute("ALTER TABLE rag_vectors ALTER COLUMN embedding TYPE vector(384)")
    op.execute("CREATE INDEX ON rag_vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")

    # Create analytics_cache table
    op.create_table('analytics_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('log_file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('log_files.id'), nullable=False),
        sa.Column('analytics_type', sa.String(100), nullable=False),
        sa.Column('analytics_data', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for analytics_cache
    op.create_index('ix_analytics_cache_project_id', 'analytics_cache', ['project_id'])
    op.create_index('ix_analytics_cache_log_file_id', 'analytics_cache', ['log_file_id'])

    # Create live_log_connections table
    op.create_table('live_log_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('connection_name', sa.String(255), nullable=False),
        sa.Column('cloud_provider', postgresql.ENUM('aws', 'azure', 'gcp', name='cloud_provider'), nullable=False),
        sa.Column('connection_config', postgresql.JSONB, nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'paused', 'error', name='connection_status'), nullable=False, default='active'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for live_log_connections
    op.create_index('ix_live_log_connections_user_id', 'live_log_connections', ['user_id'])
    op.create_index('ix_live_log_connections_project_id', 'live_log_connections', ['project_id'])
    op.create_index('ix_live_log_connections_status', 'live_log_connections', ['status'])

    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('live_connection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('live_log_connections.id'), nullable=True),
        sa.Column('alert_type', postgresql.ENUM('error_threshold', 'anomaly', 'pattern_match', name='alert_type'), nullable=False),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical', name='alert_severity'), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('is_read', sa.Boolean, nullable=False, default=False),
        sa.Column('notified_via', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for alerts
    op.create_index('ix_alerts_user_id', 'alerts', ['user_id'])
    op.create_index('ix_alerts_project_id', 'alerts', ['project_id'])
    op.create_index('ix_alerts_live_connection_id', 'alerts', ['live_connection_id'])
    op.create_index('ix_alerts_severity', 'alerts', ['severity'])
    op.create_index('ix_alerts_is_read', 'alerts', ['is_read'])
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'])

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for api_keys
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for audit_logs
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])

    # Create project_shares table
    op.create_table('project_shares',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('shared_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('shared_with_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', postgresql.ENUM('viewer', 'editor', 'admin', name='share_role'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes and constraints for project_shares
    op.create_index('ix_project_shares_project_id', 'project_shares', ['project_id'])
    op.create_index('ix_project_shares_shared_by_user_id', 'project_shares', ['shared_by_user_id'])
    op.create_index('ix_project_shares_shared_with_user_id', 'project_shares', ['shared_with_user_id'])
    op.create_unique_constraint('uq_project_share_user', 'project_shares', ['project_id', 'shared_with_user_id'])

    # Create webhooks table
    op.create_table('webhooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('url', sa.Text, nullable=False),
        sa.Column('events', postgresql.JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('secret_key', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for webhooks
    op.create_index('ix_webhooks_user_id', 'webhooks', ['user_id'])
    op.create_index('ix_webhooks_project_id', 'webhooks', ['project_id'])
    op.create_index('ix_webhooks_is_active', 'webhooks', ['is_active'])

    # Create usage_tracking table
    op.create_table('usage_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('llm_tokens_used', sa.BigInteger, nullable=False, default=0),
        sa.Column('api_calls_count', sa.Integer, nullable=False, default=0),
        sa.Column('storage_used_bytes', sa.BigInteger, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes and constraints for usage_tracking
    op.create_index('ix_usage_tracking_user_id', 'usage_tracking', ['user_id'])
    op.create_index('ix_usage_tracking_date', 'usage_tracking', ['date'])
    op.create_unique_constraint('uq_usage_tracking_user_date', 'usage_tracking', ['user_id', 'date'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('usage_tracking')
    op.drop_table('webhooks')
    op.drop_table('project_shares')
    op.drop_table('audit_logs')
    op.drop_table('api_keys')
    op.drop_table('alerts')
    op.drop_table('live_log_connections')
    op.drop_table('analytics_cache')
    op.drop_table('rag_vectors')
    op.drop_table('log_entries')
    op.drop_table('log_files')
    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('projects')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS share_role")
    op.execute("DROP TYPE IF EXISTS alert_severity")
    op.execute("DROP TYPE IF EXISTS alert_type")
    op.execute("DROP TYPE IF EXISTS connection_status")
    op.execute("DROP TYPE IF EXISTS cloud_provider")
    op.execute("DROP TYPE IF EXISTS log_level")
    op.execute("DROP TYPE IF EXISTS upload_status")
    op.execute("DROP TYPE IF EXISTS message_role")
    op.execute("DROP TYPE IF EXISTS llm_model")
    op.execute("DROP TYPE IF EXISTS subscription_tier")
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "timescaledb"')
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
