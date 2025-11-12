-- Document Parser Fillable Schema
-- Table for storing extracted fields from OCR/document processing
-- Database: Neon PostgreSQL

-- Drop table if exists (for clean reinstall)
-- DROP TABLE IF EXISTS doc_parser_fillable;

-- Create main table
CREATE TABLE IF NOT EXISTS doc_parser_fillable (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Document identifiers
    doc_id UUID NOT NULL,
    filename TEXT,
    document_type TEXT,

    -- Field data
    field_name TEXT NOT NULL,
    field_value TEXT,
    matched_field TEXT,
    confidence NUMERIC(3,2),

    -- Source data
    source_text TEXT,

    -- Timestamps
    parsed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_doc_parser_doc_id
    ON doc_parser_fillable(doc_id);

CREATE INDEX IF NOT EXISTS idx_doc_parser_filename
    ON doc_parser_fillable(filename);

CREATE INDEX IF NOT EXISTS idx_doc_parser_document_type
    ON doc_parser_fillable(document_type);

CREATE INDEX IF NOT EXISTS idx_doc_parser_matched_field
    ON doc_parser_fillable(matched_field);

CREATE INDEX IF NOT EXISTS idx_doc_parser_parsed_at
    ON doc_parser_fillable(parsed_at DESC);

CREATE INDEX IF NOT EXISTS idx_doc_parser_confidence
    ON doc_parser_fillable(confidence DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_doc_parser_type_confidence
    ON doc_parser_fillable(document_type, confidence DESC);

CREATE INDEX IF NOT EXISTS idx_doc_parser_doc_field
    ON doc_parser_fillable(doc_id, matched_field);

-- Add comments for documentation
COMMENT ON TABLE doc_parser_fillable IS
    'Stores extracted fields from document OCR processing';

COMMENT ON COLUMN doc_parser_fillable.doc_id IS
    'UUID identifying the source document';

COMMENT ON COLUMN doc_parser_fillable.filename IS
    'Original filename of the processed document';

COMMENT ON COLUMN doc_parser_fillable.document_type IS
    'Type of document: stop_loss, spd, 834, etc.';

COMMENT ON COLUMN doc_parser_fillable.field_name IS
    'Original field label as extracted from document';

COMMENT ON COLUMN doc_parser_fillable.field_value IS
    'Extracted value for the field';

COMMENT ON COLUMN doc_parser_fillable.matched_field IS
    'Normalized schema field name (snake_case)';

COMMENT ON COLUMN doc_parser_fillable.confidence IS
    'Confidence score (0.00 to 1.00) for the extraction';

COMMENT ON COLUMN doc_parser_fillable.source_text IS
    'Original OCR text (truncated if necessary)';

COMMENT ON COLUMN doc_parser_fillable.parsed_at IS
    'Timestamp when the field was parsed';

-- Create a view for high-confidence fields only
CREATE OR REPLACE VIEW doc_parser_high_confidence AS
SELECT
    id,
    doc_id,
    filename,
    document_type,
    field_name,
    field_value,
    matched_field,
    confidence,
    parsed_at
FROM doc_parser_fillable
WHERE confidence >= 0.80
ORDER BY confidence DESC, parsed_at DESC;

-- Create a view for document summaries
CREATE OR REPLACE VIEW doc_parser_summary AS
SELECT
    doc_id,
    filename,
    document_type,
    COUNT(*) as field_count,
    COUNT(CASE WHEN confidence >= 0.80 THEN 1 END) as high_confidence_count,
    AVG(confidence) as avg_confidence,
    MIN(parsed_at) as first_parsed,
    MAX(parsed_at) as last_parsed
FROM doc_parser_fillable
GROUP BY doc_id, filename, document_type
ORDER BY last_parsed DESC;

-- Create function to get all fields for a document
CREATE OR REPLACE FUNCTION get_document_fields(p_doc_id UUID)
RETURNS TABLE (
    field_name TEXT,
    field_value TEXT,
    matched_field TEXT,
    confidence NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dpf.field_name,
        dpf.field_value,
        dpf.matched_field,
        dpf.confidence
    FROM doc_parser_fillable dpf
    WHERE dpf.doc_id = p_doc_id
    ORDER BY dpf.confidence DESC, dpf.field_name;
END;
$$ LANGUAGE plpgsql;

-- Create function to get fields by type and confidence
CREATE OR REPLACE FUNCTION get_fields_by_type_and_confidence(
    p_document_type TEXT,
    p_min_confidence NUMERIC DEFAULT 0.80
)
RETURNS TABLE (
    doc_id UUID,
    filename TEXT,
    field_name TEXT,
    field_value TEXT,
    matched_field TEXT,
    confidence NUMERIC,
    parsed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dpf.doc_id,
        dpf.filename,
        dpf.field_name,
        dpf.field_value,
        dpf.matched_field,
        dpf.confidence,
        dpf.parsed_at
    FROM doc_parser_fillable dpf
    WHERE dpf.document_type = p_document_type
      AND dpf.confidence >= p_min_confidence
    ORDER BY dpf.confidence DESC, dpf.parsed_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_doc_parser_fillable_updated_at
    BEFORE UPDATE ON doc_parser_fillable
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sample queries for reference
/*
-- Get all fields for a specific document
SELECT * FROM get_document_fields('your-uuid-here');

-- Get high-confidence stop-loss fields
SELECT * FROM get_fields_by_type_and_confidence('stop_loss', 0.80);

-- Get document summary
SELECT * FROM doc_parser_summary;

-- Get all high-confidence fields
SELECT * FROM doc_parser_high_confidence;

-- Count documents by type
SELECT
    document_type,
    COUNT(DISTINCT doc_id) as document_count,
    COUNT(*) as field_count,
    AVG(confidence) as avg_confidence
FROM doc_parser_fillable
GROUP BY document_type;

-- Get fields with low confidence (need review)
SELECT
    filename,
    field_name,
    field_value,
    confidence
FROM doc_parser_fillable
WHERE confidence < 0.60
ORDER BY confidence ASC;

-- Get most recent documents
SELECT DISTINCT ON (doc_id)
    doc_id,
    filename,
    document_type,
    parsed_at
FROM doc_parser_fillable
ORDER BY doc_id, parsed_at DESC;
*/

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT ON doc_parser_fillable TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE doc_parser_fillable_id_seq TO your_app_user;
-- GRANT SELECT ON doc_parser_high_confidence TO your_app_user;
-- GRANT SELECT ON doc_parser_summary TO your_app_user;
