"""
Parser Tool API Routes
Exposes endpoints for OCR, field extraction, and data promotion.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import json
import logging
from datetime import datetime

# Import core parser modules
from .core.field_extractor import FieldExtractor
from .core.store_and_promote import save_to_neon, save_to_firebase, trigger_n8n_webhook

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/parser", tags=["parser"])

# Initialize field extractor
field_extractor = FieldExtractor()

# Load field mapping configuration
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "core", "field_mapping.json")
with open(MAPPING_FILE, "r") as f:
    field_mapping = json.load(f)


# ==================== Request/Response Models ====================

class ExtractRequest(BaseModel):
    """Request model for field extraction"""
    text: str = Field(..., description="Raw text to extract fields from")
    doc_id: Optional[str] = Field(None, description="Optional document ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class ExtractResponse(BaseModel):
    """Response model for field extraction"""
    success: bool
    doc_id: Optional[str]
    fields: Dict[str, Any]
    field_count: int
    confidence_avg: float
    categories: Dict[str, List[str]]
    metadata: Dict[str, Any]


class PromoteRequest(BaseModel):
    """Request model for promoting fields to external systems"""
    doc_id: str = Field(..., description="Document ID")
    fields: Dict[str, Any] = Field(..., description="Extracted fields to promote")
    destinations: List[str] = Field(
        default=["neon"],
        description="Destinations: 'neon', 'firebase', 'n8n'"
    )
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PromoteResponse(BaseModel):
    """Response model for promotion"""
    success: bool
    doc_id: str
    results: Dict[str, Any]
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str
    dependencies: Dict[str, str]


# ==================== API Endpoints ====================

@router.post("/extract", response_model=ExtractResponse, status_code=status.HTTP_200_OK)
async def extract_fields(request: ExtractRequest):
    """
    Extract structured fields from raw text using pattern recognition.

    This endpoint:
    1. Accepts raw text (from OCR or direct input)
    2. Applies field extraction patterns
    3. Maps extracted fields to schema
    4. Returns structured data with confidence scores

    Example:
        POST /api/parser/extract
        {
            "text": "Policy Number: ABC123\\nEffective Date: 01/01/2024\\nStop-Loss Deductible: $50,000",
            "doc_id": "doc_2024_001"
        }
    """
    try:
        logger.info(f"Extracting fields for doc_id: {request.doc_id}")

        # Extract fields with context
        extraction_result = field_extractor.extract_fields_with_context(
            text=request.text,
            field_mapping=field_mapping["mappings"]
        )

        # Calculate statistics
        fields = extraction_result.get("fields", {})
        field_count = len(fields)

        # Calculate average confidence
        confidences = [f.get("confidence", 0.0) for f in fields.values() if isinstance(f, dict)]
        confidence_avg = sum(confidences) / len(confidences) if confidences else 0.0

        # Build response
        response = ExtractResponse(
            success=True,
            doc_id=request.doc_id,
            fields=fields,
            field_count=field_count,
            confidence_avg=round(confidence_avg, 2),
            categories=extraction_result.get("categories", {}),
            metadata={
                "extraction_time": datetime.utcnow().isoformat(),
                "text_length": len(request.text),
                "mapping_version": field_mapping.get("version", "1.0.0"),
                **request.context
            }
        )

        logger.info(f"Successfully extracted {field_count} fields")
        return response

    except Exception as e:
        logger.error(f"Field extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Field extraction failed: {str(e)}"
        )


@router.post("/promote", response_model=PromoteResponse, status_code=status.HTTP_200_OK)
async def promote_fields(request: PromoteRequest):
    """
    Promote extracted fields to external systems (Neon DB, Firebase, n8n).

    This endpoint:
    1. Accepts structured field data
    2. Pushes to specified destinations
    3. Triggers webhooks/workflows
    4. Returns success status per destination

    Destinations:
    - "neon": PostgreSQL database (Neon)
    - "firebase": Firestore NoSQL database
    - "n8n": Webhook automation platform

    Example:
        POST /api/parser/promote
        {
            "doc_id": "doc_2024_001",
            "fields": { "policy_number": "ABC123", "effective_date": "2024-01-01" },
            "destinations": ["neon", "n8n"]
        }
    """
    try:
        logger.info(f"Promoting doc_id: {request.doc_id} to {request.destinations}")

        results = {}

        # Promote to Neon (PostgreSQL)
        if "neon" in request.destinations:
            try:
                neon_result = await save_to_neon(
                    doc_id=request.doc_id,
                    fields=request.fields,
                    metadata=request.metadata
                )
                results["neon"] = {
                    "success": True,
                    "message": "Saved to Neon database",
                    "details": neon_result
                }
                logger.info(f"Successfully saved to Neon: {request.doc_id}")
            except Exception as e:
                logger.error(f"Neon promotion failed: {str(e)}")
                results["neon"] = {
                    "success": False,
                    "error": str(e)
                }

        # Promote to Firebase
        if "firebase" in request.destinations:
            try:
                firebase_result = await save_to_firebase(
                    doc_id=request.doc_id,
                    fields=request.fields,
                    metadata=request.metadata
                )
                results["firebase"] = {
                    "success": True,
                    "message": "Saved to Firebase",
                    "details": firebase_result
                }
                logger.info(f"Successfully saved to Firebase: {request.doc_id}")
            except Exception as e:
                logger.error(f"Firebase promotion failed: {str(e)}")
                results["firebase"] = {
                    "success": False,
                    "error": str(e)
                }

        # Trigger n8n webhook
        if "n8n" in request.destinations:
            try:
                n8n_result = await trigger_n8n_webhook(
                    doc_id=request.doc_id,
                    fields=request.fields,
                    metadata=request.metadata
                )
                results["n8n"] = {
                    "success": True,
                    "message": "Webhook triggered",
                    "details": n8n_result
                }
                logger.info(f"Successfully triggered n8n webhook: {request.doc_id}")
            except Exception as e:
                logger.error(f"n8n webhook failed: {str(e)}")
                results["n8n"] = {
                    "success": False,
                    "error": str(e)
                }

        # Check overall success
        all_success = all(r.get("success", False) for r in results.values())

        response = PromoteResponse(
            success=all_success,
            doc_id=request.doc_id,
            results=results,
            timestamp=datetime.utcnow().isoformat()
        )

        return response

    except Exception as e:
        logger.error(f"Promotion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Promotion failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for parser service.

    Returns:
    - Service status
    - Dependency availability (Neon, Firebase, n8n)
    - Version information

    Example:
        GET /api/parser/health
    """
    try:
        # Check dependencies
        dependencies = {}

        # Check Neon connection
        neon_url = os.getenv("NEON_URL")
        dependencies["neon"] = "configured" if neon_url else "not_configured"

        # Check Firebase credentials
        firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
        dependencies["firebase"] = "configured" if firebase_creds else "not_configured"

        # Check n8n webhook URL
        n8n_webhook = os.getenv("N8N_DOC_WEBHOOK_URL")
        dependencies["n8n"] = "configured" if n8n_webhook else "not_configured"

        # Check field mapping file
        dependencies["field_mapping"] = "loaded" if field_mapping else "missing"

        response = HealthResponse(
            status="healthy",
            service="parser",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat(),
            dependencies=dependencies
        )

        return response

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


# ==================== Additional Utility Endpoints ====================

@router.get("/mappings", status_code=status.HTTP_200_OK)
async def get_field_mappings():
    """
    Get available field mappings.

    Returns the current field mapping configuration used for extraction.
    """
    try:
        return JSONResponse(content=field_mapping)
    except Exception as e:
        logger.error(f"Failed to retrieve mappings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve mappings: {str(e)}"
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_status():
    """
    Get parser service status and statistics.
    """
    try:
        return JSONResponse(content={
            "service": "parser",
            "status": "active",
            "version": "1.0.0",
            "endpoints": {
                "extract": "/api/parser/extract",
                "promote": "/api/parser/promote",
                "health": "/api/parser/health",
                "mappings": "/api/parser/mappings"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to retrieve status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}"
        )
