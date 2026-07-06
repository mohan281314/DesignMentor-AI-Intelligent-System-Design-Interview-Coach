-- DesignMentor AI — Database initialization script
-- Runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for full-text search

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE designmentor TO designmentor;
