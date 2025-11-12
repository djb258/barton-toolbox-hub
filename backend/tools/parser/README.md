# Parser Tool

**Branch:** `tool/parser`
**Location:** `/backend/tools/parser`
**Version:** 1.0.0

## Overview

The Parser Tool is a self-contained module within the Barton Toolbox Hub that provides advanced OCR (Optical Character Recognition), field extraction, and data promotion capabilities. It processes documents (PDFs, images), extracts structured fields, maps them to standardized schemas, and promotes data to external systems.

## Features

- **Field Extraction**: Extract structured fields from raw text using pattern recognition
- **Schema Mapping**: Map 150+ field variations to standardized schema fields
- **Multi-Destination Promotion**: Push data to Neon (PostgreSQL), Firebase, or n8n workflows
- **Confidence Scoring**: Confidence ratings (0.0-1.0) for each extracted field
- **Categorization**: Automatic categorization of fields (financial, coverage, dates, etc.)
- **OCR Integration**: DeepSeek-OCR support for advanced document processing

## Architecture

```
/backend/tools/parser/
├── core/
│   ├── field_extractor.py         # Field extraction engine (5 pattern types)
│   ├── field_mapping.json         # 150+ field-to-schema mappings
│   ├── store_and_promote.py       # Multi-destination data promotion
│   ├── run_dpsk_ocr_pdf.py        # DeepSeek-OCR wrapper
│   └── __init__.py
├── sql/
│   └── doc_parser_fillable_schema.sql  # Database schema
├── tests/
│   └── (test files)
├── routes.py                      # FastAPI endpoints
├── __init__.py
├── .env.example                   # Environment configuration template
└── README.md                      # This file
```

## API Endpoints

### 1. Extract Fields

Extract structured fields from raw text.

**Endpoint:** `POST /api/parser/extract`

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

**Response:**
```json
{
  "success": true,
  "doc_id": "doc_2024_001",
  "fields": {
    "policy_number": {
      "value": "ABC123",
      "confidence": 0.95,
      "source": "document"
    },
    "effective_date": {
      "value": "2024-01-01",
      "confidence": 0.90,
      "source": "document"
    },
    "stop_loss_deductible": {
      "value": 50000,
      "confidence": 0.85,
      "source": "document"
    }
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

### 2. Promote Fields

Promote extracted fields to external systems (Neon, Firebase, n8n).

**Endpoint:** `POST /api/parser/promote`

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

**Response:**
```json
{
  "success": true,
  "doc_id": "doc_2024_001",
  "results": {
    "neon": {
      "success": true,
      "message": "Saved to Neon database",
      "details": {
        "row_id": 12345
      }
    },
    "n8n": {
      "success": true,
      "message": "Webhook triggered",
      "details": {
        "workflow_id": "wf_789"
      }
    }
  },
  "timestamp": "2024-11-12T12:00:00Z"
}
```

### 3. Health Check

Check parser service health and dependency status.

**Endpoint:** `GET /api/parser/health`

**Response:**
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

### 4. Get Field Mappings

Retrieve available field mapping configuration.

**Endpoint:** `GET /api/parser/mappings`

**Response:**
```json
{
  "description": "Field label to schema field mappings",
  "version": "1.0.0",
  "mappings": {
    "stop-loss deductible": "stop_loss_deductible",
    "contract type": "contract_type",
    "policy number": "policy_number",
    ...
  }
}
```

### 5. Service Status

Get parser service status and available endpoints.

**Endpoint:** `GET /api/parser/status`

**Response:**
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

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
NEON_URL=postgresql://user:pass@host/db?sslmode=require

# Optional
FIREBASE_CREDENTIALS=/path/to/firebase-creds.json
N8N_DOC_WEBHOOK_URL=https://n8n.example.com/webhook/doc-parser

# Processing
MAX_FILE_SIZE_MB=50
OCR_TIMEOUT_SECONDS=300
MIN_CONFIDENCE_THRESHOLD=0.5
```

See `.env.example` for full configuration options.

## Field Extraction Patterns

The parser uses 5 different extraction patterns:

1. **Colon Separator**: `Field: Value`
2. **Equals/Dash**: `Field = Value` or `Field - Value`
3. **Dollar Amount**: `Field $25,000`
4. **Table Extraction**: Multi-column data
5. **Date Extraction**: Multiple date formats (MM/DD/YYYY, YYYY-MM-DD, etc.)

## Field Categories

Extracted fields are automatically categorized:

- **Financial**: Premiums, deductibles, fees
- **Coverage**: Benefits, limits, exclusions
- **Dates**: Effective dates, renewal dates, expiration
- **Contract**: Policy numbers, carriers, TPAs
- **Members**: Enrollment counts, lives covered
- **Employer**: Company info, SIC codes, addresses
- **Contact**: Phone, email, addresses

## Database Schema

The parser uses PostgreSQL (Neon) with the following schema:

```sql
CREATE TABLE doc_parser_fillable (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(255) UNIQUE NOT NULL,
    fields JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

See `sql/doc_parser_fillable_schema.sql` for complete schema.

## Integration with Barton Toolbox Hub

### Registering Routes

To integrate the parser tool into the main FastAPI application:

```python
# In main FastAPI app (e.g., backend/main.py)
from backend.tools.parser import router as parser_router

app = FastAPI()
app.include_router(parser_router)  # Adds /api/parser/* endpoints
```

### Conditional Loading

Only register parser routes if the tool is active:

```python
ENABLE_PARSER = os.getenv("ENABLE_PARSER", "true").lower() == "true"

if ENABLE_PARSER:
    from backend.tools.parser import router as parser_router
    app.include_router(parser_router)
```

## Dependencies

The parser tool requires:

```txt
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# Database
asyncpg>=0.29.0              # Neon (PostgreSQL)
psycopg2-binary>=2.9.9

# HTTP
httpx>=0.25.0                # n8n webhooks

# Firebase (optional)
firebase-admin>=6.3.0

# OCR (optional)
torch>=2.0.0
transformers>=4.35.0
pillow>=10.0.0
opencv-python>=4.8.0

# PDF Processing (optional)
pypdf2>=3.0.0
pdfplumber>=0.10.3
```

## Usage Examples

### Python Client

```python
import httpx

# Extract fields
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/parser/extract",
        json={
            "text": "Policy Number: ABC123\nEffective Date: 01/01/2024",
            "doc_id": "doc_001"
        }
    )
    result = response.json()
    print(f"Extracted {result['field_count']} fields")

# Promote fields
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/parser/promote",
        json={
            "doc_id": "doc_001",
            "fields": result["fields"],
            "destinations": ["neon", "n8n"]
        }
    )
    print(response.json())
```

### cURL

```bash
# Extract fields
curl -X POST http://localhost:8000/api/parser/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Policy Number: ABC123",
    "doc_id": "doc_001"
  }'

# Health check
curl http://localhost:8000/api/parser/health
```

## Testing

```bash
# Run parser tests
pytest backend/tools/parser/tests/

# Run with coverage
pytest backend/tools/parser/tests/ --cov=backend.tools.parser
```

## Logging

The parser logs all operations:

```python
import logging
logger = logging.getLogger(__name__)

# Logs include:
# - Field extraction attempts
# - Promotion results
# - Error details
# - Performance metrics
```

Configure log level in `.env`:
```
LOG_LEVEL=INFO
```

## Error Handling

All endpoints return structured error responses:

```json
{
  "detail": "Field extraction failed: Invalid input text",
  "status_code": 500
}
```

Common errors:
- `400`: Invalid request data
- `500`: Extraction/promotion failure
- `503`: Service unavailable (health check failure)

## Performance Considerations

- Field extraction: ~100-500ms for typical documents
- Database promotion: ~50-200ms per destination
- Webhook triggers: ~100-300ms (depends on n8n response time)
- Batch processing: Support for multiple documents via repeated calls

## Security

- Environment variables for sensitive credentials
- No hardcoded secrets
- SSL required for database connections
- Input validation via Pydantic models
- Sanitized error messages (no credential leakage)

## Roadmap

- [ ] Batch extraction endpoint
- [ ] OCR file upload support (POST /api/parser/ocr)
- [ ] Real-time validation during extraction
- [ ] Custom field mapping templates
- [ ] Advanced confidence tuning
- [ ] Webhook retry logic with exponential backoff

## Support

For issues or questions:
- GitHub Issues: [barton-toolbox-hub/issues](https://github.com/djb258/barton-toolbox-hub/issues)
- Documentation: See `/backend/tools/parser/sql/` for database schema
- Source: [mapping-app-orbt](https://github.com/djb258/mapping-app-orbt)

## License

Part of Barton Toolbox Hub - see main repository for license details.

---

**Last Updated:** 2024-11-12
**Maintainer:** Barton Toolbox Team
