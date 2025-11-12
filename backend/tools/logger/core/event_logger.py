"""
Event Logger
Logs document processing events to Neon (PostgreSQL) with Firebase failover.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import asyncpg
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventLevel(str, Enum):
    """Event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(str, Enum):
    """Common event types"""
    DOCUMENT_UPLOADED = "document_uploaded"
    PARSING_STARTED = "parsing_started"
    PARSING_COMPLETED = "parsing_completed"
    PARSING_FAILED = "parsing_failed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_FAILED = "validation_failed"
    PROMOTION_STARTED = "promotion_started"
    PROMOTION_COMPLETED = "promotion_completed"
    PROMOTION_FAILED = "promotion_failed"
    CUSTOM = "custom"


class EventLogger:
    """
    Event logger with Neon (PostgreSQL) primary storage and Firebase failover.
    """

    def __init__(self):
        self.neon_url = os.getenv("NEON_URL")
        self.firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
        self.neon_pool: Optional[asyncpg.Pool] = None
        self.firebase_client = None

        # Feature flags
        self.enable_neon = os.getenv("ENABLE_NEON", "true").lower() == "true"
        self.enable_firebase = os.getenv("ENABLE_FIREBASE", "false").lower() == "true"

    async def initialize(self):
        """Initialize database connections"""
        if self.enable_neon and self.neon_url:
            try:
                self.neon_pool = await asyncpg.create_pool(
                    dsn=self.neon_url,
                    min_size=1,
                    max_size=10
                )
                logger.info("✓ Connected to Neon database")
            except Exception as e:
                logger.error(f"✗ Failed to connect to Neon: {e}")

        if self.enable_firebase and self.firebase_credentials:
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore

                if not firebase_admin._apps:
                    cred = credentials.Certificate(self.firebase_credentials)
                    firebase_admin.initialize_app(cred)

                self.firebase_client = firestore.client()
                logger.info("✓ Connected to Firebase Firestore")
            except Exception as e:
                logger.error(f"✗ Failed to connect to Firebase: {e}")

    async def close(self):
        """Close database connections"""
        if self.neon_pool:
            await self.neon_pool.close()
            logger.info("Closed Neon connection")

    async def log_event(
        self,
        event_type: str,
        doc_id: str,
        message: str,
        level: str = EventLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an event to Neon with Firebase failover.

        Args:
            event_type: Type of event (e.g., "parsing_started")
            doc_id: Document ID associated with this event
            message: Human-readable event message
            level: Event severity level (debug, info, warning, error, critical)
            metadata: Additional metadata as JSON

        Returns:
            {
                "success": bool,
                "event_id": str,
                "storage": "neon" | "firebase" | "both",
                "timestamp": str
            }
        """
        timestamp = datetime.utcnow()
        event_data = {
            "event_type": event_type,
            "doc_id": doc_id,
            "message": message,
            "level": level,
            "metadata": metadata or {},
            "timestamp": timestamp
        }

        result = {
            "success": False,
            "event_id": None,
            "storage": None,
            "timestamp": timestamp.isoformat(),
            "errors": []
        }

        # Try Neon first
        if self.enable_neon and self.neon_pool:
            try:
                event_id = await self._log_to_neon(event_data)
                result["success"] = True
                result["event_id"] = event_id
                result["storage"] = "neon"
                logger.info(f"✓ Event logged to Neon: {event_id}")
                return result
            except Exception as e:
                error_msg = f"Neon logging failed: {str(e)}"
                logger.error(f"✗ {error_msg}")
                result["errors"].append(error_msg)

        # Failover to Firebase
        if self.enable_firebase and self.firebase_client:
            try:
                event_id = await self._log_to_firebase(event_data)
                result["success"] = True
                result["event_id"] = event_id
                result["storage"] = "firebase"
                logger.warning(f"⚠ Event logged to Firebase (failover): {event_id}")
                return result
            except Exception as e:
                error_msg = f"Firebase logging failed: {str(e)}"
                logger.error(f"✗ {error_msg}")
                result["errors"].append(error_msg)

        # Both failed
        if not result["success"]:
            logger.critical(f"✗ All storage backends failed for event: {event_type}")
            result["errors"].append("All storage backends failed")

        return result

    async def _log_to_neon(self, event_data: Dict[str, Any]) -> str:
        """Log event to Neon (PostgreSQL)"""
        query = """
            INSERT INTO doc_event_log (
                event_type,
                doc_id,
                message,
                level,
                metadata,
                timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING event_id
        """

        async with self.neon_pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                event_data["event_type"],
                event_data["doc_id"],
                event_data["message"],
                event_data["level"],
                event_data["metadata"],
                event_data["timestamp"]
            )
            return str(row["event_id"])

    async def _log_to_firebase(self, event_data: Dict[str, Any]) -> str:
        """Log event to Firebase Firestore"""
        # Convert datetime to ISO string for Firebase
        event_data_copy = event_data.copy()
        event_data_copy["timestamp"] = event_data["timestamp"].isoformat()

        # Add to Firestore
        doc_ref = self.firebase_client.collection("doc_event_log").add(event_data_copy)
        return doc_ref[1].id

    async def get_events_by_doc(
        self,
        doc_id: str,
        level: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events for a specific document.

        Args:
            doc_id: Document ID to filter by
            level: Optional event level filter
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of event dictionaries
        """
        # Try Neon first
        if self.enable_neon and self.neon_pool:
            try:
                return await self._get_events_from_neon(doc_id, level, limit, offset)
            except Exception as e:
                logger.error(f"Failed to retrieve from Neon: {e}")

        # Fallback to Firebase
        if self.enable_firebase and self.firebase_client:
            try:
                return await self._get_events_from_firebase(doc_id, level, limit, offset)
            except Exception as e:
                logger.error(f"Failed to retrieve from Firebase: {e}")

        return []

    async def _get_events_from_neon(
        self,
        doc_id: str,
        level: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Retrieve events from Neon"""
        if level:
            query = """
                SELECT
                    event_id,
                    event_type,
                    doc_id,
                    message,
                    level,
                    metadata,
                    timestamp
                FROM doc_event_log
                WHERE doc_id = $1 AND level = $2
                ORDER BY timestamp DESC
                LIMIT $3 OFFSET $4
            """
            params = (doc_id, level, limit, offset)
        else:
            query = """
                SELECT
                    event_id,
                    event_type,
                    doc_id,
                    message,
                    level,
                    metadata,
                    timestamp
                FROM doc_event_log
                WHERE doc_id = $1
                ORDER BY timestamp DESC
                LIMIT $2 OFFSET $3
            """
            params = (doc_id, limit, offset)

        async with self.neon_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def _get_events_from_firebase(
        self,
        doc_id: str,
        level: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Retrieve events from Firebase"""
        query = self.firebase_client.collection("doc_event_log").where("doc_id", "==", doc_id)

        if level:
            query = query.where("level", "==", level)

        query = query.order_by("timestamp", direction="DESCENDING").limit(limit).offset(offset)

        docs = query.stream()
        return [{"event_id": doc.id, **doc.to_dict()} for doc in docs]

    async def get_statistics(self, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get logging statistics.

        Args:
            doc_id: Optional document ID to filter statistics

        Returns:
            Statistics dictionary with event counts by level and type
        """
        if self.enable_neon and self.neon_pool:
            try:
                return await self._get_statistics_from_neon(doc_id)
            except Exception as e:
                logger.error(f"Failed to get statistics from Neon: {e}")

        return {
            "total_events": 0,
            "by_level": {},
            "by_type": {},
            "doc_id": doc_id
        }

    async def _get_statistics_from_neon(self, doc_id: Optional[str]) -> Dict[str, Any]:
        """Get statistics from Neon"""
        if doc_id:
            query = """
                SELECT
                    COUNT(*) as total_events,
                    COUNT(*) FILTER (WHERE level = 'debug') as debug_count,
                    COUNT(*) FILTER (WHERE level = 'info') as info_count,
                    COUNT(*) FILTER (WHERE level = 'warning') as warning_count,
                    COUNT(*) FILTER (WHERE level = 'error') as error_count,
                    COUNT(*) FILTER (WHERE level = 'critical') as critical_count
                FROM doc_event_log
                WHERE doc_id = $1
            """
            params = (doc_id,)
        else:
            query = """
                SELECT
                    COUNT(*) as total_events,
                    COUNT(*) FILTER (WHERE level = 'debug') as debug_count,
                    COUNT(*) FILTER (WHERE level = 'info') as info_count,
                    COUNT(*) FILTER (WHERE level = 'warning') as warning_count,
                    COUNT(*) FILTER (WHERE level = 'error') as error_count,
                    COUNT(*) FILTER (WHERE level = 'critical') as critical_count
                FROM doc_event_log
            """
            params = ()

        async with self.neon_pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)

            return {
                "total_events": row["total_events"],
                "by_level": {
                    "debug": row["debug_count"],
                    "info": row["info_count"],
                    "warning": row["warning_count"],
                    "error": row["error_count"],
                    "critical": row["critical_count"]
                },
                "doc_id": doc_id
            }


# Global logger instance
_event_logger: Optional[EventLogger] = None


async def get_event_logger() -> EventLogger:
    """Get or create the global event logger instance"""
    global _event_logger
    if _event_logger is None:
        _event_logger = EventLogger()
        await _event_logger.initialize()
    return _event_logger
