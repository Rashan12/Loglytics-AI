# Loglytics AI Database Schema

This document describes the comprehensive PostgreSQL database schema for the Loglytics AI platform, including pgvector and TimescaleDB extensions for advanced log analysis capabilities.

## Overview

The database is designed for:
- **Multi-tenant architecture** with Row-Level Security (RLS)
- **Time-series data** with TimescaleDB for log entries
- **AI/ML capabilities** with pgvector for semantic search
- **Scalable performance** with optimized indexes
- **Data isolation** with comprehensive RLS policies

## Database Name
`loglytics_db`

## Extensions Required

- **uuid-ossp**: UUID generation
- **vector**: AI embeddings and similarity search
- **timescaledb**: Time-series data optimization
- **pg_trgm**: Text search optimization

## Schema Design

### Core Tables

#### 1. Users (`users`)
- **Primary Key**: UUID
- **Features**: Multi-tier subscriptions, LLM model selection
- **Security**: RLS enabled, users can only access their own data

#### 2. Projects (`projects`)
- **Primary Key**: UUID
- **Features**: Project-based organization, sharing capabilities
- **Security**: RLS with project sharing support

#### 3. Chats (`chats`)
- **Primary Key**: UUID
- **Features**: AI chat sessions linked to projects
- **Security**: RLS based on project access

#### 4. Messages (`messages`)
- **Primary Key**: UUID
- **Features**: Chat messages with metadata
- **Security**: RLS based on chat access

### Log Management Tables

#### 5. Log Files (`log_files`)
- **Primary Key**: UUID
- **Features**: File upload tracking, S3 integration
- **Security**: RLS based on project access

#### 6. Log Entries (`log_entries`) - TimescaleDB Hypertable
- **Primary Key**: UUID
- **Features**: Time-series log data, automatic partitioning
- **Security**: RLS based on project access
- **Optimization**: Hypertable on timestamp column

### AI/ML Tables

#### 7. RAG Vectors (`rag_vectors`)
- **Primary Key**: UUID
- **Features**: Vector embeddings for semantic search
- **Security**: RLS based on project access
- **Optimization**: pgvector indexes for similarity search

#### 8. Analytics Cache (`analytics_cache`)
- **Primary Key**: UUID
- **Features**: Cached analytics results
- **Security**: RLS based on project access

### Monitoring & Alerts

#### 9. Live Log Connections (`live_log_connections`)
- **Primary Key**: UUID
- **Features**: Cloud provider integrations
- **Security**: RLS based on project access

#### 10. Alerts (`alerts`)
- **Primary Key**: UUID
- **Features**: Real-time alerting system
- **Security**: RLS based on user access

### Security & Audit

#### 11. API Keys (`api_keys`)
- **Primary Key**: UUID
- **Features**: API authentication
- **Security**: RLS based on user access

#### 12. Audit Logs (`audit_logs`)
- **Primary Key**: UUID
- **Features**: User action tracking
- **Security**: RLS based on user access

### Collaboration

#### 13. Project Shares (`project_shares`)
- **Primary Key**: UUID
- **Features**: Project sharing with role-based access
- **Security**: RLS with sharing permissions

#### 14. Webhooks (`webhooks`)
- **Primary Key**: UUID
- **Features**: Event-driven integrations
- **Security**: RLS based on project access

### Usage Tracking

#### 15. Usage Tracking (`usage_tracking`)
- **Primary Key**: UUID
- **Features**: Resource usage monitoring
- **Security**: RLS based on user access

## Key Features

### Row-Level Security (RLS)
- **Multi-tenant isolation**: Users can only access their own data
- **Project-based sharing**: Controlled access to shared projects
- **Role-based permissions**: Viewer, Editor, Admin roles
- **Comprehensive policies**: All tables protected with RLS

### Performance Optimizations
- **TimescaleDB hypertables**: Automatic partitioning for log entries
- **Vector indexes**: Optimized similarity search with pgvector
- **Composite indexes**: Optimized for common query patterns
- **Partial indexes**: Optimized for filtered queries
- **Materialized views**: Pre-computed dashboard statistics

### Data Types
- **UUIDs**: All primary keys use UUID for security
- **Enums**: Type-safe status and category fields
- **JSONB**: Flexible metadata storage
- **Timestamps**: Timezone-aware timestamps
- **Vectors**: 384-dimensional embeddings for AI

## Setup Instructions

### 1. Prerequisites
```bash
# Install PostgreSQL with extensions
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Install TimescaleDB
wget https://packagecloud.io/install/repositories/timescale/timescaledb/script.deb.sh
sudo bash script.deb.sh
sudo apt-get install timescaledb-2-postgresql-15

# Install pgvector
sudo apt-get install postgresql-15-pgvector
```

### 2. Database Setup
```bash
# Run the setup script
cd backend
python setup_database.py

# Or run manually
psql -U postgres -f sql/enable_extensions.sql
psql -U postgres -d loglytics_db -f sql/setup_database.sql
psql -U postgres -d loglytics_db -f sql/rls_policies.sql
psql -U postgres -d loglytics_db -f sql/performance_indexes.sql
```

### 3. Alembic Migrations
```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations
alembic upgrade head
```

## Security Considerations

### Authentication Integration
The database includes placeholder functions for auth system integration:
- `auth.uid()`: Returns current user UUID
- `user_has_project_access()`: Checks project access
- `get_user_project_role()`: Returns user's role in project

### Data Encryption
- **API Keys**: Stored as hashes
- **Connection Configs**: Encrypted JSONB fields
- **Audit Logs**: Include IP addresses and metadata

### Access Control
- **RLS Policies**: Comprehensive row-level security
- **Function Security**: SECURITY DEFINER functions
- **Schema Isolation**: Separate auth schema

## Performance Monitoring

### Query Optimization
- **EXPLAIN ANALYZE**: Use for query optimization
- **Index Usage**: Monitor with pg_stat_user_indexes
- **Table Statistics**: Monitor with pg_stat_user_tables

### Maintenance
- **VACUUM**: Regular maintenance for log_entries table
- **REINDEX**: Periodic index rebuilding
- **Statistics Update**: Regular ANALYZE operations

## Backup and Recovery

### Backup Strategy
```bash
# Full database backup
pg_dump -U postgres -d loglytics_db > backup.sql

# TimescaleDB specific backup
pg_dump -U postgres -d loglytics_db --schema-only > schema.sql
pg_dump -U postgres -d loglytics_db --data-only > data.sql
```

### Recovery
```bash
# Restore from backup
psql -U postgres -d loglytics_db < backup.sql
```

## Monitoring Queries

### System Health
```sql
-- Check TimescaleDB status
SELECT * FROM timescaledb_information.hypertables;

-- Check vector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check RLS status
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' AND rowsecurity = true;
```

### Performance Metrics
```sql
-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Troubleshooting

### Common Issues
1. **Extension not found**: Ensure extensions are installed
2. **RLS blocking queries**: Check user permissions
3. **TimescaleDB errors**: Verify hypertable creation
4. **Vector search slow**: Check vector indexes

### Debug Commands
```sql
-- Check current user
SELECT auth.uid();

-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'projects';

-- Check table permissions
SELECT * FROM information_schema.table_privileges 
WHERE table_name = 'projects';
```

## Future Enhancements

### Planned Features
- **Partitioning**: Additional partitioning strategies
- **Compression**: TimescaleDB compression for old data
- **Replication**: Read replicas for scaling
- **Monitoring**: Automated performance monitoring

### Scalability Considerations
- **Sharding**: Horizontal scaling strategies
- **Caching**: Redis integration for hot data
- **Archiving**: Cold storage for historical data
- **Load Balancing**: Connection pooling strategies






