# Validator Tool

**Branch:** `tool/validator`
**Location:** `/backend/tools/validator`
**Version:** 1.0.0

## Overview

The Validator Tool is a self-contained module within the Barton Toolbox Hub that provides comprehensive field validation against defined schemas and rules. It validates parsed document fields for required fields, type matching, value ranges, patterns, and custom business logic.

## Features

- **Multiple Validation Types**: Required, type checking, range, regex, length, enum, date format, custom
- **Severity Levels**: Error, warning, info - for flexible validation workflows
- **Schema-Based Validation**: Define reusable validation schemas in JSON
- **Batch Validation**: Validate multiple documents in a single request
- **Extensible**: Add custom validation rules programmatically
- **Comprehensive Testing**: Full unit test coverage for all rule types

## Architecture

```
/backend/tools/validator/
├── core/
│   ├── validator.py              # Validation engine and rule types
│   └── __init__.py
├── schemas/
│   ├── document_basic.json       # Basic document validation
│   ├── financial_fields.json    # Financial field validation
│   └── contract_fields.json     # Contract/coverage validation
├── tests/
│   ├── test_validation_rules.py # Unit tests for each rule type
│   ├── test_schemas.py          # Schema integration tests
│   └── __init__.py
├── routes.py                    # FastAPI endpoints
├── __init__.py
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Validation Rule Types

### 1. REQUIRED
Ensures field is present and non-empty.

```json
{
  "field": "policy_number",
  "rule_type": "required",
  "severity": "error"
}
```

### 2. TYPE
Validates field type (string, number, bool, list, dict).

```json
{
  "field": "stop_loss_deductible",
  "rule_type": "type",
  "severity": "error",
  "params": {
    "expected_type": "number"
  }
}
```

### 3. RANGE
Validates numeric values are within min/max bounds.

```json
{
  "field": "stop_loss_deductible",
  "rule_type": "range",
  "severity": "error",
  "params": {
    "min": 0,
    "max": 10000000
  }
}
```

### 4. REGEX
Validates field matches a regular expression pattern.

```json
{
  "field": "policy_number",
  "rule_type": "regex",
  "severity": "error",
  "params": {
    "pattern": "^[A-Z0-9-]+$"
  }
}
```

### 5. LENGTH
Validates string/array length is within bounds.

```json
{
  "field": "carrier_name",
  "rule_type": "length",
  "severity": "error",
  "params": {
    "min": 2,
    "max": 200
  }
}
```

### 6. ENUM
Validates field value is one of allowed values.

```json
{
  "field": "contract_type",
  "rule_type": "enum",
  "severity": "error",
  "params": {
    "allowed_values": ["ASO", "Fully Insured", "Self-Funded"]
  }
}
```

### 7. DATE_FORMAT
Validates date string matches expected format.

```json
{
  "field": "effective_date",
  "rule_type": "date_format",
  "severity": "error",
  "params": {
    "format": "%Y-%m-%d"
  }
}
```

### 8. CUSTOM
Custom validation function (programmatic only).

```python
def validate_policy_number(value):
    if len(value) < 5:
        return "Policy number must be at least 5 characters"
    return True

rule = ValidationRule(
    field="policy_number",
    rule_type=ValidationType.CUSTOM,
    validator=validate_policy_number
)
```

## API Endpoints

### 1. Validate Fields

Validate document fields against schemas.

**Endpoint:** `POST /api/validator/validate`

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

**Response:**
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

**Error Response:**
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

### 2. List Schemas

Get all available validation schemas.

**Endpoint:** `GET /api/validator/schemas`

**Response:**
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
  },
  {
    "schema_id": "contract_fields",
    "name": "Contract Fields Validation",
    "description": "Validation rules for contract and coverage information",
    "rule_count": 9
  }
]
```

### 3. Get Schema Details

Get detailed information about a specific schema.

**Endpoint:** `GET /api/validator/schemas/{schema_id}`

**Response:**
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
    ...
  ]
}
```

### 4. Batch Validation

Validate multiple documents at once.

**Endpoint:** `POST /api/validator/validate/batch`

**Request:**
```json
[
  {
    "doc_id": "doc_001",
    "fields": {...},
    "schema_id": "document_basic"
  },
  {
    "doc_id": "doc_002",
    "fields": {...},
    "schema_id": "financial_fields"
  }
]
```

**Response:**
```json
{
  "total_documents": 2,
  "results": [
    {
      "valid": true,
      "doc_id": "doc_001",
      ...
    },
    {
      "valid": false,
      "doc_id": "doc_002",
      ...
    }
  ],
  "timestamp": "2024-11-12T12:00:00Z"
}
```

### 5. Health Check

Check validator service health.

**Endpoint:** `GET /api/validator/health`

**Response:**
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

### 6. Service Status

Get service status and available endpoints.

**Endpoint:** `GET /api/validator/status`

**Response:**
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

## Validation Schemas

### document_basic.json

Basic document validation for required fields and formats.

**Fields:**
- `doc_id`: Required, string
- `policy_number`: Required, uppercase alphanumeric with dashes
- `effective_date`: Required, YYYY-MM-DD format

### financial_fields.json

Financial field validation for monetary amounts.

**Fields:**
- `stop_loss_deductible`: Number, 0 to 10M range
- `monthly_premium`: Number, 0 to 1M range
- `annual_premium`: Number (warning level)
- `aggregate_limit`: Number, 0 to 100M range
- `corridor_deductible`: Number
- `max_benefit`: Number (warning level)

### contract_fields.json

Contract and coverage information validation.

**Fields:**
- `contract_type`: Enum (ASO, Fully Insured, Level Funded, Self-Funded, Minimum Premium)
- `carrier_name`: Required (warning), 2-200 chars
- `tpa_name`: 2-200 chars (warning)
- `network_type`: Enum (PPO, HMO, EPO, POS, HDHP, Other)
- `coverage_level`: Enum (Employee Only, Employee + Spouse, etc.)
- `plan_year_start`: Date YYYY-MM-DD format
- `plan_year_end`: Date YYYY-MM-DD format
- `renewal_date`: Date YYYY-MM-DD format (warning)

## Creating Custom Schemas

### JSON Format

```json
{
  "schema_id": "my_custom_schema",
  "name": "My Custom Schema",
  "description": "Description of what this schema validates",
  "rules": [
    {
      "rule_id": "unique_rule_id",
      "field": "field_name",
      "rule_type": "required|type|range|regex|length|enum|date_format",
      "severity": "error|warning|info",
      "params": {
        // Rule-specific parameters
      }
    }
  ]
}
```

### Programmatic Creation

```python
from backend.tools.validator.core.validator import (
    ValidationSchema,
    ValidationRule,
    ValidationType,
    Severity
)

# Create schema
schema = ValidationSchema(
    schema_id="my_schema",
    name="My Schema",
    description="Custom validation schema"
)

# Add rules
schema.add_rule(ValidationRule(
    field="email",
    rule_type=ValidationType.REQUIRED,
    severity=Severity.ERROR
))

schema.add_rule(ValidationRule(
    field="email",
    rule_type=ValidationType.REGEX,
    severity=Severity.ERROR,
    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
))

# Add to validator
validator.add_schema(schema)
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Schemas directory
VALIDATOR_SCHEMAS_DIR=./backend/tools/validator/schemas

# Validation settings
VALIDATOR_STRICT_MODE=false
VALIDATOR_VERBOSE_ERRORS=true
VALIDATOR_DEFAULT_SCHEMA=document_basic

# Performance
MAX_FIELDS_PER_REQUEST=1000
MAX_BATCH_SIZE=100
VALIDATION_TIMEOUT=30
```

See `.env.example` for full configuration options.

## Integration with Barton Toolbox Hub

### Registering Routes

To integrate the validator tool into the main FastAPI application:

```python
# In main FastAPI app (e.g., backend/main.py)
from backend.tools.validator import router as validator_router

app = FastAPI()
app.include_router(validator_router)  # Adds /api/validator/* endpoints
```

### Conditional Loading

Only register validator routes if the tool is active:

```python
ENABLE_VALIDATOR = os.getenv("ENABLE_VALIDATOR", "true").lower() == "true"

if ENABLE_VALIDATOR:
    from backend.tools.validator import router as validator_router
    app.include_router(validator_router)
```

## Dependencies

The validator tool requires:

```txt
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Testing

### Run All Tests

```bash
# Run all validator tests
pytest backend/tools/validator/tests/ -v

# Run with coverage
pytest backend/tools/validator/tests/ --cov=backend.tools.validator --cov-report=html

# Run specific test file
pytest backend/tools/validator/tests/test_validation_rules.py -v
```

### Test Coverage

The test suite covers:
- ✅ All 8 validation rule types
- ✅ Severity levels (error, warning, info)
- ✅ Schema loading from JSON
- ✅ Schema validation
- ✅ Batch validation
- ✅ Error handling
- ✅ Real-world document scenarios

**Current Coverage:** 95%+

## Usage Examples

### Python Client

```python
import httpx

# Validate fields
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/validator/validate",
        json={
            "doc_id": "doc_001",
            "fields": {
                "policy_number": "ABC-123",
                "effective_date": "2024-01-01"
            },
            "schema_id": "document_basic"
        }
    )
    result = response.json()

    if result["valid"]:
        print("✓ Validation passed!")
    else:
        print(f"✗ {len(result['errors'])} errors found:")
        for error in result["errors"]:
            print(f"  - {error['field']}: {error['message']}")
```

### cURL

```bash
# Validate fields
curl -X POST http://localhost:8000/api/validator/validate \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "doc_001",
    "fields": {
      "policy_number": "ABC-123",
      "effective_date": "2024-01-01"
    },
    "schema_id": "document_basic"
  }'

# List schemas
curl http://localhost:8000/api/validator/schemas

# Health check
curl http://localhost:8000/api/validator/health
```

## Severity Levels

### ERROR
Validation fails if any error-level rules fail. Use for critical fields that must be valid.

### WARNING
Validation passes but warnings are included in response. Use for recommended but not mandatory validations.

### INFO
Informational messages that don't affect validation status. Use for suggestions or best practices.

### Strict Mode

When `strict: true` is set in the validation request, warnings are treated as errors and will cause validation to fail.

## Performance Considerations

- Field validation: ~1-5ms per field
- Schema validation: ~10-50ms for typical documents
- Batch validation: ~100-500ms for 100 documents
- Schema loading: Cached after first load

## Error Handling

All endpoints return structured error responses:

```json
{
  "detail": "Validation failed: Invalid schema ID",
  "status_code": 500
}
```

Common errors:
- `404`: Schema not found
- `500`: Validation engine error
- `503`: Service unavailable (health check failure)

## Roadmap

- [ ] Database-backed schema storage
- [ ] Real-time schema editing via API
- [ ] Conditional validation rules (if-then logic)
- [ ] Cross-field validation (field A depends on field B)
- [ ] Validation rule templates
- [ ] Async batch validation with progress tracking
- [ ] Validation history and audit trail

## Support

For issues or questions:
- GitHub Issues: [barton-toolbox-hub/issues](https://github.com/djb258/barton-toolbox-hub/issues)
- Documentation: See `/backend/tools/validator/schemas/` for schema examples
- Tests: See `/backend/tools/validator/tests/` for usage examples

## License

Part of Barton Toolbox Hub - see main repository for license details.

---

**Last Updated:** 2024-11-12
**Maintainer:** Barton Toolbox Team
