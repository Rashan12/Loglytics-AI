-- Enable required PostgreSQL extensions for Loglytics AI
-- Run this script as a superuser before running migrations

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for AI embeddings
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable TimescaleDB for time-series data
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Verify extensions are installed
SELECT extname, extversion 
FROM pg_extension 
WHERE extname IN ('uuid-ossp', 'vector', 'timescaledb');

-- Create the database if it doesn't exist
-- Note: This needs to be run as a superuser
-- CREATE DATABASE loglytics_db;
