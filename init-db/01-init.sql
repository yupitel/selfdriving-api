-- Initialize database for selfdriving application
-- This script is executed when PostgreSQL container is first created

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS selfdriving;

-- Set default search path
ALTER DATABASE selfdriving SET search_path TO selfdriving, public;

-- Grant permissions (adjust as needed)
GRANT ALL ON SCHEMA selfdriving TO postgres;
GRANT CREATE ON SCHEMA selfdriving TO postgres;