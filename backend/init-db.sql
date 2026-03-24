-- ============================================================================
-- Ooumph SHG Database Initialization Script
-- ============================================================================
-- This script is automatically run when PostgreSQL container starts
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For composite indexes

-- Create schema if not exists (using public by default)
-- Schema: public

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ooumph_shg TO ooumph;
GRANT ALL PRIVILEGES ON SCHEMA public TO ooumph;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ooumph;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ooumph;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ooumph;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO ooumph;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Ooumph SHG Database initialized successfully';
END $$;
