# Logger Tool

**Branch:** `tool/logger`
**Location:** `/backend/tools/logger`
**Version:** 1.0.0

## Overview

The Logger Tool is a self-contained module within the Barton Toolbox Hub that provides robust event logging for document processing workflows. It logs events to Neon (PostgreSQL) as primary storage with automatic failover to Firebase (Firestore) if Neon is unavailable.

## Features

- **Dual Storage**: Primary Neon (PostgreSQL) + Firebase (Firestore) failover
- **Event Levels**: Debug, info, warning, error, critical
- **Document Tracking**: All events linked to document IDs
- **Rich Metadata**: Store custom JSON metadata with each event
- **Statistics**: Event counts and breakdowns by level
- **Batch Logging**: Log multiple events in a single request
- **SQL Schema**: Production-ready schema with indexes and views
- **Automatic Failover**: Seamless fallback when primary storage fails

## Architecture

```
/backend/tools/logger/
├── core/
│   ├── event_logger.py          # Event logging engine with failover
│   └── __init__.py
├── sql/
│   └── doc_event_log_schema.sql # PostgreSQL schema (reference)
├── tests/
│   └── (test files)
├── routes.py                    # FastAPI endpoints
├── __init__.py
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Event Levels

| Level    | Description                          | Use Case                          |
|----------|--------------------------------------|-----------------------------------|
| DEBUG    | Detailed debugging information       | Development, troubleshooting      |
| INFO     | General informational messages       | Normal operations, milestones     |
| WARNING  | Warning messages (non-critical)      | Potential issues, deprecated APIs |
| ERROR    | Error messages (processing failures) | Failed operations, validation errors |
| CRITICAL | Critical system failures             | System crashes, data corruption   |

## Common Event Types

| Event Type              | Description                        |
|-------------------------|------------------------------------|
| document_uploaded       | Document uploaded to system        |
| parsing_started         | OCR/parsing initiated              |
| parsing_completed       | Parsing finished successfully      |
| parsing_failed          | Parsing failed                     |
| validation_started      | Field validation initiated         |
| validation_completed    | Validation passed                  |
| validation_failed       | Validation failed                  |
| promotion_started       | Data promotion initiated           |
| promotion_completed     | Data promoted to external systems  |
| promotion_failed        | Promotion failed                   |
| custom                  | Custom event types                 |

## API Endpoints

### 1. Log Event

Log a single event for a document.

**Endpoint:** `POST /api/logger/event`

**Request:**
```json
{
  "event_type": "parsing_completed",
  "doc_id": "doc_2024_001",
  "message": "Successfully parsed document with 25 fields extracted",
  "level": "info",
  "metadata": {
    "field_count": 25,
    "confidence_avg": 0.92,
    "processing_time_ms": 1250
  }
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "12345",
  "storage": "neon",
  "timestamp": "2024-11-12T12:00:00Z",
  "errors": []
}
```

### 2. Get Events by Document

Retrieve all events for a specific document.

**Endpoint:** `GET /api/logger/events/{doc_id}`

**Query Parameters:**
- `level` (optional): Filter by event level
- `limit` (default: 100, max: 1000): Max events to return
- `offset` (default: 0): Pagination offset

**Example:**
```
GET /api/logger/events/doc_2024_001?level=error&limit=50
```

**Response:**
```json
{
  "doc_id": "doc_2024_001",
  "total_count": 3,
  "events": [
    {
      "event_id": "12345",
      "event_type": "parsing_failed",
      "doc_id": "doc_2024_001",
      "message": "Failed to extract fields: Invalid PDF format",
      "level": "error",
      "metadata": {
        "error_code": "PDF_001"
      },
      "timestamp": "2024-11-12T12:00:00Z"
    }
  ],
  "level_filter": "error",
  "limit": 50,
  "offset": 0
}
```

### 3. Get Statistics

Get logging statistics (overall or for a specific document).

**Endpoint:** `GET /api/logger/statistics`

**Query Parameters:**
- `doc_id` (optional): Filter by document ID

**Example:**
```
GET /api/logger/statistics?doc_id=doc_2024_001
```

**Response:**
```json
{
  "total_events": 150,
  "by_level": {
    "debug": 10,
    "info": 120,
    "warning": 15,
    "error": 4,
    "critical": 1
  },
  "doc_id": "doc_2024_001",
  "timestamp": "2024-11-12T12:00:00Z"
}
```

### 4. Batch Log Events

Log multiple events in a single request.

**Endpoint:** `POST /api/logger/events/batch`

**Request:**
```json
[
  {
    "event_type": "parsing_started",
    "doc_id": "doc_001",
    "message": "Started parsing",
    "level": "info"
  },
  {
    "event_type": "parsing_completed",
    "doc_id": "doc_001",
    "message": "Parsing completed",
    "level": "info"
  }
]
```

**Response:**
```json
{
  "total_events": 2,
  "results": [
    {
      "success": true,
      "event_id": "12345",
      "storage": "neon",
      "timestamp": "2024-11-12T12:00:00Z"
    },
    {
      "success": true,
      "event_id": "12346",
      "storage": "neon",
      "timestamp": "2024-11-12T12:00:01Z"
    }
  ],
  "timestamp": "2024-11-12T12:00:01Z"
}
```

### 5. Health Check

Check logger service health and storage backend status.

**Endpoint:** `GET /api/logger/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "logger",
  "version": "1.0.0",
  "timestamp": "2024-11-12T12:00:00Z",
  "storage_backends": {
    "neon": "connected",
    "firebase": "disabled"
  }
}
```

### 6. Service Status

Get service status and available endpoints.

**Endpoint:** `GET /api/logger/status`

**Response:**
```json
{
  "service": "logger",
  "status": "active",
  "version": "1.0.0",
  "endpoints": {
    "log_event": "/api/logger/event",
    "get_events": "/api/logger/events/{doc_id}",
    "statistics": "/api/logger/statistics",
    "health": "/api/logger/health"
  },
  "timestamp": "2024-11-12T12:00:00Z"
}
```

## Storage Architecture

### Primary: Neon (PostgreSQL)

**Advantages:**
- SQL queries and complex filtering
- ACID compliance
- Indexes for fast retrieval
- Views and functions for analytics
- Mature ecosystem

**Table:** `doc_event_log`

### Failover: Firebase (Firestore)

**Advantages:**
- Real-time sync
- High availability
- Offline support
- Easy mobile integration

**Collection:** `doc_event_log`

### Failover Logic

```
1. Attempt to log to Neon
   ├─ Success → Return Neon event_id
   └─ Failure → Try Firebase
       ├─ Success → Return Firebase doc_id
       └─ Failure → Return error
```

## Database Schema

The SQL schema is provided as a **reference file** at `sql/doc_event_log_schema.sql`.

**To set up the database manually:**

```bash
# Connect to your Neon database
psql $NEON_URL -f backend/tools/logger/sql/doc_event_log_schema.sql
```

**Schema Features:**
- ✅ Main table: `doc_event_log`
- ✅ Indexes on: doc_id, event_type, level, timestamp
- ✅ GIN index for JSONB metadata
- ✅ Views: `recent_errors`, `recent_doc_events`, `event_type_stats`
- ✅ Functions: `cleanup_old_events()`, `get_doc_event_summary()`

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Primary storage
NEON_URL=postgresql://user:pass@host/db?sslmode=require

# Failover storage (optional)
FIREBASE_CREDENTIALS=/path/to/firebase-creds.json

# Feature flags
ENABLE_NEON=true
ENABLE_FIREBASE=false

# Retention
EVENT_RETENTION_DAYS=90
AUTO_CLEANUP_ENABLED=false
```

See `.env.example` for full configuration options.

## Integration with Barton Toolbox Hub

### Registering Routes

To integrate the logger tool into the main FastAPI application:

```python
# In main FastAPI app (e.g., backend/main.py)
from backend.tools.logger import router as logger_router

app = FastAPI()
app.include_router(logger_router)  # Adds /api/logger/* endpoints

# Initialize logger on startup
@app.on_event("startup")
async def startup():
    from backend.tools.logger.core import get_event_logger
    await get_event_logger()

# Close connections on shutdown
@app.on_event("shutdown")
async def shutdown():
    from backend.tools.logger.core import get_event_logger
    logger = await get_event_logger()
    await logger.close()
```

### Conditional Loading

Only register logger routes if the tool is active:

```python
ENABLE_LOGGER = os.getenv("ENABLE_LOGGER", "true").lower() == "true"

if ENABLE_LOGGER:
    from backend.tools.logger import router as logger_router
    app.include_router(logger_router)
```

## Usage in Other Tools

### Log Events from Parser Tool

```python
from backend.tools.logger.core import get_event_logger

# Get logger instance
event_logger = await get_event_logger()

# Log parsing started
await event_logger.log_event(
    event_type="parsing_started",
    doc_id="doc_001",
    message="Started parsing PDF document",
    level="info",
    metadata={"filename": "contract.pdf", "size_bytes": 125000}
)

# Log parsing completed
await event_logger.log_event(
    event_type="parsing_completed",
    doc_id="doc_001",
    message="Parsing completed successfully",
    level="info",
    metadata={"field_count": 25, "processing_time_ms": 1250}
)

# Log parsing error
await event_logger.log_event(
    event_type="parsing_failed",
    doc_id="doc_001",
    message="Failed to parse: Invalid PDF format",
    level="error",
    metadata={"error_code": "PDF_001", "error_details": "..."}
)
```

### Log Events from Validator Tool

```python
# Log validation started
await event_logger.log_event(
    event_type="validation_started",
    doc_id="doc_001",
    message="Started field validation",
    level="info",
    metadata={"schema_id": "document_basic", "field_count": 25}
)

# Log validation completed
await event_logger.log_event(
    event_type="validation_completed",
    doc_id="doc_001",
    message="Validation passed",
    level="info",
    metadata={"errors": 0, "warnings": 2}
)

# Log validation failed
await event_logger.log_event(
    event_type="validation_failed",
    doc_id="doc_001",
    message="Validation failed with 3 errors",
    level="error",
    metadata={"error_count": 3, "errors": [...]}
)
```

## Dependencies

The logger tool requires:

```txt
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0

# Database
asyncpg>=0.29.0              # Neon (PostgreSQL)

# Firebase (Optional)
firebase-admin>=6.3.0

# Utilities
python-dotenv==1.0.0         # Environment variables
```

## SQL Queries

### Get All Events for a Document

```sql
SELECT * FROM doc_event_log
WHERE doc_id = 'doc_2024_001'
ORDER BY timestamp DESC;
```

### Get Errors for a Document

```sql
SELECT * FROM doc_event_log
WHERE doc_id = 'doc_2024_001'
  AND level IN ('error', 'critical')
ORDER BY timestamp DESC;
```

### Get Event Timeline

```sql
SELECT event_type, level, message, timestamp
FROM doc_event_log
WHERE doc_id = 'doc_2024_001'
ORDER BY timestamp ASC;
```

### Count Events by Level

```sql
SELECT level, COUNT(*)
FROM doc_event_log
GROUP BY level
ORDER BY COUNT(*) DESC;
```

### Recent Errors (Last Hour)

```sql
SELECT doc_id, message, timestamp
FROM doc_event_log
WHERE level = 'error'
  AND timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

### Documents with Errors (Last 24 Hours)

```sql
SELECT DISTINCT doc_id, COUNT(*) as error_count
FROM doc_event_log
WHERE level IN ('error', 'critical')
  AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY doc_id
ORDER BY error_count DESC;
```

### Event Rate (Events per Minute, Last Hour)

```sql
SELECT DATE_TRUNC('minute', timestamp) as minute, COUNT(*) as event_count
FROM doc_event_log
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY minute
ORDER BY minute DESC;
```

### Cleanup Old Events

```sql
-- Delete events older than 90 days
SELECT cleanup_old_events(90);
```

### Document Event Summary

```sql
-- Get summary for a document
SELECT * FROM get_doc_event_summary('doc_2024_001');
```

## Performance Considerations

- Event logging: ~10-50ms per event
- Neon writes: ~20-100ms
- Firebase writes: ~100-300ms
- Batch logging: ~100-500ms for 100 events
- Query retrieval: ~10-100ms (with indexes)

## Error Handling

All endpoints return structured error responses:

```json
{
  "detail": "Event logging failed: Database connection error",
  "status_code": 500
}
```

Common errors:
- `500`: Logging failure (both backends failed)
- `503`: Service unavailable (no backends configured)

## Monitoring

### Key Metrics to Monitor

1. **Event Rate**: Events logged per minute/hour
2. **Error Rate**: Percentage of failed logging attempts
3. **Failover Rate**: How often Firebase failover is triggered
4. **Storage Distribution**: Neon vs Firebase event counts
5. **Query Performance**: Average query response times

### Alerts

Set up alerts for:
- High error event rates (>10% of total events)
- Logging failures (both backends failing)
- High failover rates (Neon frequently unavailable)
- Database size growing too fast

## Maintenance

### Regular Tasks

1. **Analyze table** (weekly):
   ```sql
   ANALYZE doc_event_log;
   ```

2. **Clean up old logs** (monthly):
   ```sql
   SELECT cleanup_old_events(90);  -- Keep last 90 days
   ```

3. **Check table size**:
   ```sql
   SELECT pg_size_pretty(pg_total_relation_size('doc_event_log'));
   ```

4. **Vacuum** (as needed):
   ```sql
   VACUUM ANALYZE doc_event_log;
   ```

## Roadmap

- [ ] Event streaming (WebSocket support)
- [ ] Advanced filtering (multiple criteria)
- [ ] Event correlation (link related events)
- [ ] Alerting system (trigger alerts on patterns)
- [ ] Dashboard integration
- [ ] Export to CSV/JSON
- [ ] Event replay functionality
- [ ] Retention policies (auto-archive)

## Support

For issues or questions:
- GitHub Issues: [barton-toolbox-hub/issues](https://github.com/djb258/barton-toolbox-hub/issues)
- Documentation: See `/backend/tools/logger/sql/` for schema reference
- SQL Functions: See schema file for utility functions

## License

Part of Barton Toolbox Hub - see main repository for license details.

---

**Last Updated:** 2024-11-12
**Maintainer:** Barton Toolbox Team
