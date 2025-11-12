-- ==========================================
-- Document Event Log Schema (Neon/PostgreSQL)
-- ==========================================
-- This is a REFERENCE schema file
-- Run this manually to create the table in your Neon database
--
-- Usage:
--   psql $NEON_URL -f doc_event_log_schema.sql
-- ==========================================

-- Drop existing table (optional - comment out if you want to preserve data)
-- DROP TABLE IF EXISTS doc_event_log CASCADE;

-- Main event log table
CREATE TABLE IF NOT EXISTS doc_event_log (
    event_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    doc_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_doc_event_log_doc_id ON doc_event_log(doc_id);
CREATE INDEX IF NOT EXISTS idx_doc_event_log_event_type ON doc_event_log(event_type);
CREATE INDEX IF NOT EXISTS idx_doc_event_log_level ON doc_event_log(level);
CREATE INDEX IF NOT EXISTS idx_doc_event_log_timestamp ON doc_event_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_doc_event_log_composite ON doc_event_log(doc_id, timestamp DESC);

-- GIN index for JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_doc_event_log_metadata ON doc_event_log USING GIN(metadata);

-- Comments
COMMENT ON TABLE doc_event_log IS 'Audit log for document processing events';
COMMENT ON COLUMN doc_event_log.event_id IS 'Unique event identifier';
COMMENT ON COLUMN doc_event_log.event_type IS 'Type of event (parsing_started, validation_completed, etc.)';
COMMENT ON COLUMN doc_event_log.doc_id IS 'Associated document ID';
COMMENT ON COLUMN doc_event_log.message IS 'Human-readable event message';
COMMENT ON COLUMN doc_event_log.level IS 'Event severity: debug, info, warning, error, critical';
COMMENT ON COLUMN doc_event_log.metadata IS 'Additional event data as JSON';
COMMENT ON COLUMN doc_event_log.timestamp IS 'Event timestamp';

-- ==========================================
-- Useful Views
-- ==========================================

-- View: Recent errors
CREATE OR REPLACE VIEW recent_errors AS
SELECT
    event_id,
    event_type,
    doc_id,
    message,
    level,
    metadata,
    timestamp
FROM doc_event_log
WHERE level IN ('error', 'critical')
ORDER BY timestamp DESC
LIMIT 100;

-- View: Events by document (last 24 hours)
CREATE OR REPLACE VIEW recent_doc_events AS
SELECT
    doc_id,
    COUNT(*) as event_count,
    COUNT(*) FILTER (WHERE level = 'error') as error_count,
    COUNT(*) FILTER (WHERE level = 'warning') as warning_count,
    MAX(timestamp) as last_event
FROM doc_event_log
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY doc_id
ORDER BY last_event DESC;

-- View: Event statistics by type
CREATE OR REPLACE VIEW event_type_stats AS
SELECT
    event_type,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE level = 'error') as error_count,
    COUNT(*) FILTER (WHERE level = 'warning') as warning_count,
    COUNT(*) FILTER (WHERE level = 'info') as info_count,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen
FROM doc_event_log
GROUP BY event_type
ORDER BY total_count DESC;

-- ==========================================
-- Utility Functions
-- ==========================================

-- Function: Clean up old events
CREATE OR REPLACE FUNCTION cleanup_old_events(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM doc_event_log
    WHERE timestamp < NOW() - (days_to_keep || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_events IS 'Delete events older than specified days. Usage: SELECT cleanup_old_events(90);';

-- Function: Get document event summary
CREATE OR REPLACE FUNCTION get_doc_event_summary(target_doc_id VARCHAR)
RETURNS TABLE (
    doc_id VARCHAR,
    total_events BIGINT,
    debug_count BIGINT,
    info_count BIGINT,
    warning_count BIGINT,
    error_count BIGINT,
    critical_count BIGINT,
    first_event TIMESTAMP WITH TIME ZONE,
    last_event TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        target_doc_id::VARCHAR,
        COUNT(*),
        COUNT(*) FILTER (WHERE level = 'debug'),
        COUNT(*) FILTER (WHERE level = 'info'),
        COUNT(*) FILTER (WHERE level = 'warning'),
        COUNT(*) FILTER (WHERE level = 'error'),
        COUNT(*) FILTER (WHERE level = 'critical'),
        MIN(doc_event_log.timestamp),
        MAX(doc_event_log.timestamp)
    FROM doc_event_log
    WHERE doc_event_log.doc_id = target_doc_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_doc_event_summary IS 'Get event summary for a document. Usage: SELECT * FROM get_doc_event_summary(''doc_001'');';

-- ==========================================
-- Sample Queries
-- ==========================================

-- Get all events for a document
-- SELECT * FROM doc_event_log WHERE doc_id = 'doc_2024_001' ORDER BY timestamp DESC;

-- Get errors for a document
-- SELECT * FROM doc_event_log WHERE doc_id = 'doc_2024_001' AND level IN ('error', 'critical') ORDER BY timestamp DESC;

-- Get event timeline for a document
-- SELECT event_type, level, message, timestamp FROM doc_event_log WHERE doc_id = 'doc_2024_001' ORDER BY timestamp ASC;

-- Count events by level
-- SELECT level, COUNT(*) FROM doc_event_log GROUP BY level ORDER BY COUNT(*) DESC;

-- Recent error messages
-- SELECT doc_id, message, timestamp FROM doc_event_log WHERE level = 'error' AND timestamp >= NOW() - INTERVAL '1 hour' ORDER BY timestamp DESC;

-- Documents with errors in last 24 hours
-- SELECT DISTINCT doc_id, COUNT(*) as error_count FROM doc_event_log WHERE level IN ('error', 'critical') AND timestamp >= NOW() - INTERVAL '24 hours' GROUP BY doc_id ORDER BY error_count DESC;

-- Event rate (events per minute, last hour)
-- SELECT DATE_TRUNC('minute', timestamp) as minute, COUNT(*) as event_count FROM doc_event_log WHERE timestamp >= NOW() - INTERVAL '1 hour' GROUP BY minute ORDER BY minute DESC;

-- ==========================================
-- Maintenance
-- ==========================================

-- Run periodically to clean up old logs (keeps last 90 days)
-- SELECT cleanup_old_events(90);

-- Analyze table for query optimization
-- ANALYZE doc_event_log;

-- Check table size
-- SELECT pg_size_pretty(pg_total_relation_size('doc_event_log')) as total_size;
