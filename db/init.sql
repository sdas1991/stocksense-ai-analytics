-- Database initialization script
-- This file is executed when the PostgreSQL container first starts

-- Create database (if not using default)
-- Note: docker-compose will handle database creation

-- Execute schema
\i /docker-entrypoint-initdb.d/schema.sql

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
