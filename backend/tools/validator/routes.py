"""
Validator Tool API Routes
Exposes endpoints for field validation against defined schemas.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Import core validator
from .core.validator import FieldValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/validator", tags=["validator"])

# Initialize field validator
field_validator = FieldValidator()


# ==================== Request/Response Models ====================

class ValidateRequest(BaseModel):
    """Request model for validation"""
    doc_id: str = Field(..., description="Document ID")
    fields: Dict[str, Any] = Field(..., description="Fields to validate")
    schema_id: Optional[str] = Field(
        None,
        description="Optional schema ID. If not provided, validates against all schemas."
    )
    strict: bool = Field(
        default=False,
        description="If True, warnings are treated as errors"
    )


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str
    rule_type: str
    message: str
    severity: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    rule_id: Optional[str] = None
    timestamp: str


class ValidateResponse(BaseModel):
    """Response model for validation"""
    valid: bool
    doc_id: str
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    info: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: str


class SchemaInfo(BaseModel):
    """Schema information"""
    schema_id: str
    name: str
    description: str
    rule_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str
    schemas_loaded: int
    schemas: List[str]


# ==================== API Endpoints ====================

@router.post("/validate", response_model=ValidateResponse, status_code=status.HTTP_200_OK)
async def validate_fields(request: ValidateRequest):
    """
    Validate document fields against validation schemas.

    This endpoint:
    1. Accepts document ID and field data
    2. Validates against specified schema or all schemas
    3. Returns validation results with errors, warnings, and info messages
    4. Supports strict mode where warnings are treated as errors

    Validation Rules:
    - **required**: Field must be present and non-empty
    - **type**: Field must match expected type (string, number, bool, etc.)
    - **range**: Numeric field must fall within min/max range
    - **regex**: Field must match regular expression pattern
    - **length**: String/array length must be within min/max
    - **enum**: Field value must be one of allowed values
    - **date_format**: Field must match date format pattern

    Example:
        POST /api/validator/validate
        {
            "doc_id": "doc_2024_001",
            "fields": {
                "policy_number": "ABC123",
                "effective_date": "2024-01-01",
                "stop_loss_deductible": 50000
            },
            "schema_id": "document_basic"
        }
    """
    try:
        logger.info(f"Validating doc_id: {request.doc_id} with schema: {request.schema_id or 'all'}")

        # Perform validation
        validation_result = field_validator.validate(
            fields=request.fields,
            schema_id=request.schema_id
        )

        # Apply strict mode if requested
        if request.strict and validation_result["warnings"]:
            validation_result["errors"].extend(validation_result["warnings"])
            validation_result["warnings"] = []
            validation_result["valid"] = False

        # Build summary
        summary = {
            "total_errors": len(validation_result["errors"]),
            "total_warnings": len(validation_result["warnings"]),
            "total_info": len(validation_result["info"]),
            "fields_validated": validation_result.get("fields_validated", 0),
            "rules_checked": validation_result.get("rules_checked", 0),
            "schema_id": request.schema_id or "all",
            "strict_mode": request.strict
        }

        if "schema_name" in validation_result:
            summary["schema_name"] = validation_result["schema_name"]

        if "schemas_checked" in validation_result:
            summary["schemas_checked"] = validation_result["schemas_checked"]

        # Build response
        response = ValidateResponse(
            valid=validation_result["valid"],
            doc_id=request.doc_id,
            errors=validation_result["errors"],
            warnings=validation_result["warnings"],
            info=validation_result["info"],
            summary=summary,
            timestamp=datetime.utcnow().isoformat()
        )

        logger.info(
            f"Validation complete for {request.doc_id}: "
            f"valid={response.valid}, errors={len(response.errors)}, "
            f"warnings={len(response.warnings)}"
        )

        return response

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/schemas", response_model=List[SchemaInfo], status_code=status.HTTP_200_OK)
async def list_schemas():
    """
    List all available validation schemas.

    Returns:
        List of schemas with their metadata (ID, name, description, rule count)

    Example:
        GET /api/validator/schemas
    """
    try:
        schemas = field_validator.list_schemas()
        return [SchemaInfo(**schema) for schema in schemas]

    except Exception as e:
        logger.error(f"Failed to list schemas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schemas: {str(e)}"
        )


@router.get("/schemas/{schema_id}", status_code=status.HTTP_200_OK)
async def get_schema(schema_id: str):
    """
    Get detailed information about a specific schema.

    Args:
        schema_id: The schema ID to retrieve

    Returns:
        Schema details including all rules

    Example:
        GET /api/validator/schemas/document_basic
    """
    try:
        schema = field_validator.get_schema(schema_id)

        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema '{schema_id}' not found"
            )

        return JSONResponse(content=schema.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schema {schema_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for validator service.

    Returns:
    - Service status
    - Number of loaded schemas
    - List of available schema IDs
    - Version information

    Example:
        GET /api/validator/health
    """
    try:
        schemas = field_validator.list_schemas()
        schema_ids = [s["schema_id"] for s in schemas]

        response = HealthResponse(
            status="healthy",
            service="validator",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat(),
            schemas_loaded=len(schema_ids),
            schemas=schema_ids
        )

        return response

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_status():
    """
    Get validator service status and available endpoints.
    """
    try:
        schemas = field_validator.list_schemas()

        return JSONResponse(content={
            "service": "validator",
            "status": "active",
            "version": "1.0.0",
            "endpoints": {
                "validate": "/api/validator/validate",
                "schemas": "/api/validator/schemas",
                "schema_detail": "/api/validator/schemas/{schema_id}",
                "health": "/api/validator/health"
            },
            "schemas_available": len(schemas),
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to retrieve status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}"
        )


# ==================== Utility Endpoints ====================

@router.post("/validate/batch", status_code=status.HTTP_200_OK)
async def validate_batch(
    documents: List[ValidateRequest]
):
    """
    Validate multiple documents in a single request.

    Args:
        documents: List of validation requests

    Returns:
        List of validation results

    Example:
        POST /api/validator/validate/batch
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
    """
    try:
        results = []

        for doc in documents:
            try:
                result = await validate_fields(doc)
                results.append(result.dict())
            except Exception as e:
                results.append({
                    "valid": False,
                    "doc_id": doc.doc_id,
                    "errors": [{
                        "field": "_system",
                        "message": f"Validation error: {str(e)}",
                        "severity": "error"
                    }],
                    "warnings": [],
                    "info": [],
                    "summary": {},
                    "timestamp": datetime.utcnow().isoformat()
                })

        return JSONResponse(content={
            "total_documents": len(documents),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Batch validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch validation failed: {str(e)}"
        )
