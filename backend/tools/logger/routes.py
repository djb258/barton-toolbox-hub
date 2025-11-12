"""
Logger Tool API Routes
Exposes endpoints for event logging and retrieval.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Import core logger
from .core.event_logger import get_event_logger, EventLogger, EventLevel, EventType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/logger", tags=["logger"])


# ==================== Request/Response Models ====================

class LogEventRequest(BaseModel):
    """Request model for logging an event"""
    event_type: str = Field(..., description="Type of event (e.g., parsing_started, validation_completed)")
    doc_id: str = Field(..., description="Document ID associated with this event")
    message: str = Field(..., description="Human-readable event message")
    level: str = Field(
        default=EventLevel.INFO,
        description="Event level: debug, info, warning, error, critical"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata as JSON"
    )


class LogEventResponse(BaseModel):
    """Response model for log event"""
    success: bool
    event_id: Optional[str]
    storage: Optional[str]
    timestamp: str
    errors: List[str] = []


class EventDetail(BaseModel):
    """Event detail model"""
    event_id: str
    event_type: str
    doc_id: str
    message: str
    level: str
    metadata: Dict[str, Any]
    timestamp: str


class GetEventsResponse(BaseModel):
    """Response model for retrieving events"""
    doc_id: str
    total_count: int
    events: List[Dict[str, Any]]
    level_filter: Optional[str]
    limit: int
    offset: int


class StatisticsResponse(BaseModel):
    """Statistics response model"""
    total_events: int
    by_level: Dict[str, int]
    doc_id: Optional[str]
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str
    storage_backends: Dict[str, str]


# ==================== Dependency ====================

async def get_logger() -> EventLogger:
    """Dependency to get event logger instance"""
    return await get_event_logger()


# ==================== API Endpoints ====================

@router.post("/event", response_model=LogEventResponse, status_code=status.HTTP_201_CREATED)
async def log_event(
    request: LogEventRequest,
    event_logger: EventLogger = Depends(get_logger)
):
    """
    Log an event for a document.

    This endpoint:
    1. Accepts event data (type, doc_id, message, level, metadata)
    2. Attempts to log to Neon (PostgreSQL) first
    3. Falls back to Firebase if Neon fails
    4. Returns event ID and storage location

    Event Levels:
    - **debug**: Detailed debugging information
    - **info**: General informational messages
    - **warning**: Warning messages (non-critical issues)
    - **error**: Error messages (failures that affect processing)
    - **critical**: Critical errors (system failures)

    Common Event Types:
    - document_uploaded
    - parsing_started, parsing_completed, parsing_failed
    - validation_started, validation_completed, validation_failed
    - promotion_started, promotion_completed, promotion_failed
    - custom (for custom events)

    Example:
        POST /api/logger/event
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
    """
    try:
        logger.info(f"Logging event: {request.event_type} for doc: {request.doc_id}")

        result = await event_logger.log_event(
            event_type=request.event_type,
            doc_id=request.doc_id,
            message=request.message,
            level=request.level,
            metadata=request.metadata
        )

        response = LogEventResponse(
            success=result["success"],
            event_id=result["event_id"],
            storage=result["storage"],
            timestamp=result["timestamp"],
            errors=result.get("errors", [])
        )

        if not response.success:
            logger.error(f"Failed to log event: {response.errors}")

        return response

    except Exception as e:
        logger.error(f"Event logging failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event logging failed: {str(e)}"
        )


@router.get("/events/{doc_id}", response_model=GetEventsResponse, status_code=status.HTTP_200_OK)
async def get_events(
    doc_id: str,
    level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    event_logger: EventLogger = Depends(get_logger)
):
    """
    Retrieve events for a specific document.

    Args:
        doc_id: Document ID to retrieve events for
        level: Optional filter by event level (debug, info, warning, error, critical)
        limit: Maximum number of events to return (default: 100, max: 1000)
        offset: Number of events to skip for pagination (default: 0)

    Returns:
        List of events ordered by timestamp (most recent first)

    Example:
        GET /api/logger/events/doc_2024_001?level=error&limit=50

    Response:
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
                    "metadata": {"error_code": "PDF_001"},
                    "timestamp": "2024-11-12T12:00:00Z"
                }
            ],
            "level_filter": "error",
            "limit": 50,
            "offset": 0
        }
    """
    try:
        # Validate limit
        if limit > 1000:
            limit = 1000

        logger.info(f"Retrieving events for doc: {doc_id}, level: {level}, limit: {limit}")

        events = await event_logger.get_events_by_doc(
            doc_id=doc_id,
            level=level,
            limit=limit,
            offset=offset
        )

        # Convert datetime objects to ISO strings
        for event in events:
            if "timestamp" in event and hasattr(event["timestamp"], "isoformat"):
                event["timestamp"] = event["timestamp"].isoformat()

        response = GetEventsResponse(
            doc_id=doc_id,
            total_count=len(events),
            events=events,
            level_filter=level,
            limit=limit,
            offset=offset
        )

        return response

    except Exception as e:
        logger.error(f"Failed to retrieve events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve events: {str(e)}"
        )


@router.get("/statistics", response_model=StatisticsResponse, status_code=status.HTTP_200_OK)
async def get_statistics(
    doc_id: Optional[str] = None,
    event_logger: EventLogger = Depends(get_logger)
):
    """
    Get logging statistics.

    Args:
        doc_id: Optional document ID to filter statistics

    Returns:
        Statistics including total event count and breakdown by level

    Example:
        GET /api/logger/statistics
        GET /api/logger/statistics?doc_id=doc_2024_001

    Response:
        {
            "total_events": 150,
            "by_level": {
                "debug": 10,
                "info": 120,
                "warning": 15,
                "error": 4,
                "critical": 1
            },
            "doc_id": null,
            "timestamp": "2024-11-12T12:00:00Z"
        }
    """
    try:
        logger.info(f"Getting statistics for doc: {doc_id or 'all'}")

        stats = await event_logger.get_statistics(doc_id=doc_id)

        response = StatisticsResponse(
            total_events=stats.get("total_events", 0),
            by_level=stats.get("by_level", {}),
            doc_id=doc_id,
            timestamp=datetime.utcnow().isoformat()
        )

        return response

    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(event_logger: EventLogger = Depends(get_logger)):
    """
    Health check endpoint for logger service.

    Returns:
    - Service status
    - Available storage backends (Neon, Firebase)
    - Version information

    Example:
        GET /api/logger/health
    """
    try:
        storage_backends = {}

        # Check Neon status
        if event_logger.enable_neon:
            if event_logger.neon_pool:
                storage_backends["neon"] = "connected"
            else:
                storage_backends["neon"] = "configured_but_not_connected"
        else:
            storage_backends["neon"] = "disabled"

        # Check Firebase status
        if event_logger.enable_firebase:
            if event_logger.firebase_client:
                storage_backends["firebase"] = "connected"
            else:
                storage_backends["firebase"] = "configured_but_not_connected"
        else:
            storage_backends["firebase"] = "disabled"

        response = HealthResponse(
            status="healthy",
            service="logger",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat(),
            storage_backends=storage_backends
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
    Get logger service status and available endpoints.
    """
    try:
        return JSONResponse(content={
            "service": "logger",
            "status": "active",
            "version": "1.0.0",
            "endpoints": {
                "log_event": "/api/logger/event",
                "get_events": "/api/logger/events/{doc_id}",
                "statistics": "/api/logger/statistics",
                "health": "/api/logger/health"
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to retrieve status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}"
        )


# ==================== Utility Endpoints ====================

@router.post("/events/batch", status_code=status.HTTP_201_CREATED)
async def log_events_batch(
    events: List[LogEventRequest],
    event_logger: EventLogger = Depends(get_logger)
):
    """
    Log multiple events in a single request.

    Args:
        events: List of event requests

    Returns:
        List of log results for each event

    Example:
        POST /api/logger/events/batch
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
    """
    try:
        results = []

        for event in events:
            try:
                result = await event_logger.log_event(
                    event_type=event.event_type,
                    doc_id=event.doc_id,
                    message=event.message,
                    level=event.level,
                    metadata=event.metadata
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "event_id": None,
                    "storage": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "errors": [str(e)]
                })

        return JSONResponse(content={
            "total_events": len(events),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Batch logging failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch logging failed: {str(e)}"
        )
