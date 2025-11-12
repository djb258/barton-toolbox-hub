# Barton Toolbox Hub - API Overview

**Version:** 1.0.0
**Last Updated:** 2024-11-12

Complete API reference for all tools in the Barton Toolbox Hub.

---

## Parser Tool API

**Base Path:** `/api/parser`

### Endpoints

#### 1. Extract Fields

**POST** `/api/parser/extract`

Extract structured fields from raw text using pattern recognition.

**Request:**
```json
{
  "text": "Policy Number: ABC123\nEffective Date: 01/01/2024\nStop-Loss Deductible: $50,000",
  "doc_id": "doc_2024_001",
  "context": {
    "source": "manual_upload",
    "user_id": "user_123"
  }
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "doc_id": "doc_2024_001",
  "fields": {
    "policy_number": {"value": "ABC123", "confidence": 0.95, "source": "document"},
    "effective_date": {"value": "2024-01-01", "confidence": 0.90, "source": "document"},
    "stop_loss_deductible": {"value": 50000, "confidence": 0.85, "source": "document"}
  },
  "field_count": 3,
  "confidence_avg": 0.90,
  "categories": {
    "contract": ["policy_number", "effective_date"],
    "financial": ["stop_loss_deductible"]
  },
  "metadata": {
    "extraction_time": "2024-11-12T12:00:00Z",
    "text_length": 89,
    "mapping_version": "1.0.0"
  }
}
```

#### 2. Promote Fields

**POST** `/api/parser/promote`

Promote extracted fields to external systems (Neon, Firebase, n8n).

**Request:**
```json
{
  "doc_id": "doc_2024_001",
  "fields": {
    "policy_number": "ABC123",
    "effective_date": "2024-01-01",
    "stop_loss_deductible": 50000
  },
  "destinations": ["neon", "n8n"],
  "metadata": {
    "user_id": "user_123",
    "source": "manual_upload"
  }
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "doc_id": "doc_2024_001",
  "results": {
    "neon": {
      "success": true,
      "message": "Saved to Neon database",
      "details": {"row_id": 12345}
    },
    "n8n": {
      "success": true,
      "message": "Webhook triggered",
      "details": {"workflow_id": "wf_789"}
    }
  },
  "timestamp": "2024-11-12T12:00:00Z"
}
```

#### 3. Get Field Mappings

**GET** `/api/parser/mappings`

Retrieve available field mapping configuration.

**Response:** `200 OK`
```json
{
  "description": "Field label to schema field mappings",
  "version": "1.0.0",
  "mappings": {
    "stop-loss deductible": "stop_loss_deductible",
    "contract type": "contract_type",
    "policy number": "policy_number"
  }
}
```

#### 4. Service Status

**GET** `/api/parser/status`

Get parser service status.

**Response:** `200 OK`
```json
{
  "service": "parser",
  "status": "active",
  "version": "1.0.0",
  "endpoints": {
    "extract": "/api/parser/extract",
    "promote": "/api/parser/promote",
    "health": "/api/parser/health",
    "mappings": "/api/parser/mappings"
  },
  "timestamp": "2024-11-12T12:00:00Z"
}
```

#### 5. Health Check

**GET** `/api/parser/health`

Check parser service health and dependencies.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "parser",
  "version": "1.0.0",
  "timestamp": "2024-11-12T12:00:00Z",
  "dependencies": {
    "neon": "configured",
    "firebase": "not_configured",
    "n8n": "configured",
    "field_mapping": "loaded"
  }
}
```

---

## Validator Tool API

**Base Path:** `/api/validator`

### Endpoints

#### 1. Validate Fields

**POST** `/api/validator/validate`

Validate document fields against validation schemas.

**Request:**
```json
{
  "doc_id": "doc_2024_001",
  "fields": {
    "policy_number": "ABC-123",
    "effective_date": "2024-01-01",
    "stop_loss_deductible": 50000,
    "contract_type": "Self-Funded"
  },
  "schema_id": "document_basic",
  "strict": false
}
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "doc_id": "doc_2024_001",
  "errors": [],
  "warnings": [],
  "info": [],
  "summary": {
    "total_errors": 0,
    "total_warnings": 0,
    "total_info": 0,
    "fields_validated": 4,
    "rules_checked": 6,
    "schema_id": "document_basic",
    "schema_name": "Basic Document Validation",
    "strict_mode": false
  },
  "timestamp": "2024-11-12T12:00:00Z"
}
```

**Validation Failed Response:** `200 OK`
```json
{
  "valid": false,
  "doc_id": "doc_2024_001",
  "errors": [
    {
      "field": "policy_number",
      "rule_type": "required",
      "message": "Field 'policy_number' is required",
      "severity": "error",
      "expected": "non-empty value",
      "actual": null,
      "rule_id": "policy_number_required",
      "timestamp": "2024-11-12T12:00:00Z"
    }
  ],
  "warnings": [],
  "info": [],
  "summary": {
    "total_errors": 1,
    "total_warnings": 0,
    "total_info": 0
  },
  "timestamp": "2024-11-12T12:00:00Z"
}
```

#### 2. Batch Validation

**POST** `/api/validator/validate/batch`

Validate multiple documents in a single request.

**Request:**
```json
[
  {
    "doc_id": "doc_001",
    "fields": {"policy_number": "ABC123"},
    "schema_id": "document_basic"
  },
  {
    "doc_id": "doc_002",
    "fields": {"policy_number": "XYZ789"},
    "schema_id": "financial_fields"
  }
]
```

**Response:** `200 OK`
```json
{
  "total_documents": 2,
  "results": [
    {
      "valid": true,
      "doc_id": "doc_001",
      "errors": [],
      "warnings": [],
      "summary": {...}
    },
    {
      "valid": false,
      "doc_id": "doc_002",
      "errors": [{...}],
      "warnings": [],
      "summary": {...}
    }
  ],
  "timestamp": "2024-11-12T12:00:00Z"
}
```

#### 3. List Schemas

**GET** `/api/validator/schemas`

Get all available validation schemas.

**Response:** `200 OK`
```json
[
  {
    "schema_id": "document_basic",
    "name": "Basic Document Validation",
    "description": "Basic validation rules for parsed documents",
    "rule_count": 6
  },
  {
    "schema_id": "financial_fields",
    "name": "Financial Fields Validation",
    "description": "Validation rules for financial and coverage amounts",
    "rule_count": 9
  }
]
```

#### 4. Get Schema Details

**GET** `/api/validator/schemas/{schema_id}`

Get detailed information about a specific schema.

**Response:** `200 OK`
```json
{
  "schema_id": "document_basic",
  "name": "Basic Document Validation",
  "description": "Basic validation rules for parsed documents",
  "rule_count": 6,
  "rules": [
    {
      "rule_id": "policy_number_required",
      "field": "policy_number",
      "rule_type": "required",
      "severity": "error",
      "params": {}
    },
    {
      "rule_id": "policy_number_regex",
      "field": "policy_number",
      "rule_type": "regex",
      "severity": "error",
      "params": {
        "pattern": "^[A-Z0-9-]+$"
      }
    }
  ]
}
```

#### 5. Health Check

**GET** `/api/validator/health`

Check validator service health.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "validator",
  "version": "1.0.0",
  "timestamp": "2024-11-12T12:00:00Z",
  "schemas_loaded": 3,
  "schemas": [
    "document_basic",
    "financial_fields",
    "contract_fields"
  ]
}
```

#### 6. Service Status

**GET** `/api/validator/status`

Get service status and available endpoints.

**Response:** `200 OK`
```json
{
  "service": "validator",
  "status": "active",
  "version": "1.0.0",
  "endpoints": {
    "validate": "/api/validator/validate",
    "schemas": "/api/validator/schemas",
    "schema_detail": "/api/validator/schemas/{schema_id}",
    "health": "/api/validator/health"
  },
  "schemas_available": 3,
  "timestamp": "2024-11-12T12:00:00Z"
}
```

---

## Logger Tool API

**Base Path:** `/api/logger`

### Endpoints

#### 1. Log Event

**POST** `/api/logger/event`

Log an event for a document.

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

**Response:** `201 Created`
```json
{
  "success": true,
  "event_id": "12345",
  "storage": "neon",
  "timestamp": "2024-11-12T12:00:00Z",
  "errors": []
}
```

**Failover Response:** `201 Created`
```json
{
  "success": true,
  "event_id": "fb_abc123",
  "storage": "firebase",
  "timestamp": "2024-11-12T12:00:00Z",
  "errors": ["Neon logging failed: Connection timeout"]
}
```

#### 2. Batch Log Events

**POST** `/api/logger/events/batch`

Log multiple events in a single request.

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

**Response:** `201 Created`
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

#### 3. Get Events by Document

**GET** `/api/logger/events/{doc_id}`

Retrieve events for a specific document.

**Query Parameters:**
- `level` (optional): Filter by event level
- `limit` (default: 100, max: 1000): Max events to return
- `offset` (default: 0): Pagination offset

**Example:**
```
GET /api/logger/events/doc_2024_001?level=error&limit=50
```

**Response:** `200 OK`
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

#### 4. Get Statistics

**GET** `/api/logger/statistics`

Get logging statistics (overall or for a specific document).

**Query Parameters:**
- `doc_id` (optional): Filter by document ID

**Example:**
```
GET /api/logger/statistics?doc_id=doc_2024_001
```

**Response:** `200 OK`
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

#### 5. Health Check

**GET** `/api/logger/health`

Check logger service health and storage backend status.

**Response:** `200 OK`
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

#### 6. Service Status

**GET** `/api/logger/status`

Get service status and available endpoints.

**Response:** `200 OK`
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

---

## Common Patterns

### Error Responses

All endpoints follow a standard error format:

**400 Bad Request**
```json
{
  "detail": "Invalid request: Missing required field 'doc_id'"
}
```

**404 Not Found**
```json
{
  "detail": "Schema 'invalid_schema' not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Operation failed: Database connection error"
}
```

**503 Service Unavailable**
```json
{
  "detail": "Health check failed: No storage backends available"
}
```

### Authentication

Currently, no authentication is required for API endpoints. In production:

```http
Authorization: Bearer <token>
```

### Rate Limiting

No rate limiting is currently enforced. Recommended limits:
- Parse/Validate: 100 requests/minute
- Logger: 1000 events/minute
- Batch operations: 10 requests/minute

### CORS

Configure allowed origins in `.env`:
```
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
```

---

## Complete Workflow Example

### End-to-End Document Processing

```bash
# 1. Upload and Parse Document
curl -X POST http://localhost:8000/api/parser/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Policy Number: ABC123\nEffective Date: 2024-01-01\nStop-Loss: $50,000",
    "doc_id": "doc_001"
  }'

# Response: { "fields": {...}, "doc_id": "doc_001" }

# 2. Validate Extracted Fields
curl -X POST http://localhost:8000/api/validator/validate \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "doc_001",
    "fields": {
      "policy_number": "ABC123",
      "effective_date": "2024-01-01",
      "stop_loss_deductible": 50000
    },
    "schema_id": "document_basic"
  }'

# Response: { "valid": true, "errors": [] }

# 3. Promote to External Systems
curl -X POST http://localhost:8000/api/parser/promote \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "doc_001",
    "fields": {
      "policy_number": "ABC123",
      "effective_date": "2024-01-01",
      "stop_loss_deductible": 50000
    },
    "destinations": ["neon", "n8n"]
  }'

# Response: { "success": true, "results": {...} }

# 4. Retrieve Event Log
curl http://localhost:8000/api/logger/events/doc_001

# Response: { "events": [...] }
```

---

## SDK Examples

### Python Client

```python
import httpx
import asyncio

class BartonToolboxClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def parse(self, text, doc_id):
        response = await self.client.post(
            f"{self.base_url}/api/parser/extract",
            json={"text": text, "doc_id": doc_id}
        )
        return response.json()

    async def validate(self, doc_id, fields, schema_id="document_basic"):
        response = await self.client.post(
            f"{self.base_url}/api/validator/validate",
            json={"doc_id": doc_id, "fields": fields, "schema_id": schema_id}
        )
        return response.json()

    async def promote(self, doc_id, fields, destinations=["neon"]):
        response = await self.client.post(
            f"{self.base_url}/api/parser/promote",
            json={"doc_id": doc_id, "fields": fields, "destinations": destinations}
        )
        return response.json()

    async def get_events(self, doc_id):
        response = await self.client.get(
            f"{self.base_url}/api/logger/events/{doc_id}"
        )
        return response.json()

# Usage
async def process_document():
    client = BartonToolboxClient()

    # Parse
    parse_result = await client.parse(
        text="Policy Number: ABC123\n...",
        doc_id="doc_001"
    )

    # Validate
    validate_result = await client.validate(
        doc_id="doc_001",
        fields=parse_result["fields"]
    )

    if validate_result["valid"]:
        # Promote
        promote_result = await client.promote(
            doc_id="doc_001",
            fields=parse_result["fields"],
            destinations=["neon", "n8n"]
        )

    # Get logs
    events = await client.get_events("doc_001")
    print(f"Total events: {events['total_count']}")

asyncio.run(process_document())
```

---

## Support

- **Documentation:** `/backend/docs/README.md`
- **GitHub:** [barton-toolbox-hub](https://github.com/djb258/barton-toolbox-hub)
- **Issues:** [GitHub Issues](https://github.com/djb258/barton-toolbox-hub/issues)

---

**Generated with Claude Code**
**Maintainer:** Barton Toolbox Team
